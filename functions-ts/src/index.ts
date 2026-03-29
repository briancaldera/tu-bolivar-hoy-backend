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
import { ZodError } from 'zod'
import Fastify, { FastifyRequest, FastifyReply } from 'fastify'
import {
  checkIntegrity,
  fetchExchangeRates,
  getExchangeRateForPeriod,
  getLatestExchangeRates,
} from './exchange-rate/functions'
import { UnauthenticatedError } from './auth/errors/unauthenticated-error'
import { QuotaExceededError } from './exchange-rate/errors/quota-exceeded-error'
import { createHash } from 'node:crypto'
import { AuthService } from './auth/application/auth-service'
import { createAdminSupabaseClient } from './exchange-rate/infrastructure/supabase/client'
import { logger } from 'firebase-functions/logger'

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

const app = Fastify()
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

app.addHook('preHandler', async (req: FastifyRequest, res: FastifyReply) => {
  const supabase = createAdminSupabaseClient()
  const authService = new AuthService(supabase)
  await authService.processRequest(req)
})

app.register(
  async (instance) => {
    instance.get('/latest-rates', async (req, res) => {
      const result = await getLatestExchangeRates()

      const hash = createHash('md5')
        .update(JSON.stringify(result))
        .digest('hex')

      const eTag = `"${hash}"`

      if (
        req.headers['if-none-match'] &&
        req.headers['if-none-match'] === eTag
      ) {
        logger.info(`Response not modified for etag: ${eTag}`)
        logger.info('Sending response')
        res.status(304).send()
      } else {
        logger.info('Sending response')
        res
          .header('Cache-Control', 'public, max-age=60')
          .header('ETag', eTag)
          .status(200)
          .send(result)
      }
    })
  },
  { prefix: '/v1' },
)

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
