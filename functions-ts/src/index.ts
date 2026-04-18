/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import { initializeApp } from 'firebase-admin/app'
import { onSchedule } from 'firebase-functions/scheduler'
import { onCall, onRequest } from 'firebase-functions/https'
import { z, ZodError } from 'zod'
import Fastify, { FastifyReply, FastifyRequest } from 'fastify'
import {
  checkHealth,
  checkIntegrity,
  fetchExchangeRates,
  getExchangeRateForCurrency,
  getExchangeRateForPeriod,
  getLatestExchangeRates,
} from './exchange-rate/functions'
import { UnauthenticatedError } from './auth/errors/unauthenticated-error'
import { QuotaExceededError } from './exchange-rate/errors/quota-exceeded-error'
import { AuthService } from './auth/application/auth-service'
import { createAdminSupabaseClient } from './exchange-rate/infrastructure/supabase/client'
import { logger } from 'firebase-functions/logger'
import {
  serializerCompiler,
  validatorCompiler,
  ZodTypeProvider,
} from 'fastify-type-provider-zod'
import Etag from '@fastify/etag'

initializeApp({
  storageBucket: 'tubolivarhoy.firebasestorage.app',
})

export const enqueueFetchExchangeRate = onSchedule(
  {
    maxInstances: 1,
    schedule: 'every 1 hours synchronized',
    retryCount: 5,
    minBackoffSeconds: 180,
    maxRetrySeconds: 50 * 60,
  },
  async (_event): Promise<void> => {
    await fetchExchangeRates()
  },
)

export const fetchExchangeRateForPeriod = onCall(
  {
    maxInstances: 3,
    timeoutSeconds: 2 * 60,
  },
  async (request, _response) => {
    const currency = request.data.currency
    const startTime = request.data.startDatetime
    const endTime = request.data.endDateTime

    const res = await getExchangeRateForPeriod(currency, [startTime, endTime])

    return { exchange_rate_map: Object.fromEntries(res) }
  },
)

export const integrityCheck = onSchedule(
  {
    schedule: 'every day 00:00',
    maxInstances: 1,
  },
  async (_event): Promise<void> => await checkIntegrity(),
)

const app = Fastify().withTypeProvider<ZodTypeProvider>()

app.register(Etag)

app.setValidatorCompiler(validatorCompiler)
app.setSerializerCompiler(serializerCompiler)

app.setErrorHandler((error, request, reply) => {
  if (error instanceof UnauthenticatedError) {
    logger.warn(error, request)
    return reply.status(401).send('Unauthorized')
  } else if (error instanceof ZodError) {
    logger.info(error, request)
    return reply.status(400).send('Bad request')
  } else if (error instanceof QuotaExceededError) {
    logger.info(error, request)
    return reply.status(429).send('Quota exceeded')
  } else {
    logger.error(error, request)
    return reply.status(500).send('Internal Server Error')
  }
})

app.register(
  async (instance) => {
    instance.addHook(
      'preHandler',
      async (req: FastifyRequest, res: FastifyReply) => {
        const supabase = createAdminSupabaseClient()
        const authService = new AuthService(supabase)
        await authService.processRequest(req)
      },
    )

    instance.get('/latest-rates', async (req, res) => {
      const result = await getLatestExchangeRates()

      res.header('cache-control', 'private, max-age=60')
      return result
    })

    instance.withTypeProvider<ZodTypeProvider>().get(
      '/currency/:currency',
      {
        schema: {
          params: z.object({
            currency: z.enum(['usd', 'eur', 'try', 'rub', 'cny']),
          }),
          querystring: z.object({
            datetime: z.iso.date().optional(),
          }),
        },
      },
      async (req, res) => {
        const result = await getExchangeRateForCurrency(req.params.currency)

        res.header('cache-control', 'private, max-age=60')

        return {
          rate: result,
        }
      },
    )
  },
  { prefix: '/v1' },
)

app.get('/health', {}, async (_, res) => {
  const status = await checkHealth()

  res.header('cache-control', 'public, max-age=180')

  if (status) {
    return {
      status: 'pass',
    }
  } else {
    return {
      status: 'fail',
    }
  }
})

export const api = onRequest(
  {
    cors: true,
    timeoutSeconds: 30,
    region: 'us-east4',
    maxInstances: 3,
    minInstances: 0,
    serviceAccount: 'api-service-agent@tubolivarhoy.iam.gserviceaccount.com',
  },
  async (req, res) => {
    await app.ready()
    logger.info('Request received...', req)
    app.server.emit('request', req, res)
  },
)
