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
import {
  checkIntegrity,
  fetchExchangeRates,
  getExchangeRateForPeriod,
  getLatestExchangeRates,
} from './exchange-rate/functions'
import { UnauthenticatedError } from './auth/errors/unauthenticated-error'
import { QuotaExceededError } from './exchange-rate/errors/quota-exceeded-error'
import { createHash } from 'node:crypto'

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

export const latest_exchange_rates = onRequest(
  { cors: true },
  async (req, res): Promise<void> => {
    try {
      switch (req.method) {
        case 'GET':
          const result = await getLatestExchangeRates(req)

          const hash = createHash('md5')
            .update(JSON.stringify(result))
            .digest('hex')

          const eTag = `"${hash}"`

          if (
            req.headers['if-none-match'] &&
            req.headers['if-none-match'] === eTag
          ) {
            res.status(304)
          } else {
            res
              .setHeader('Cache-Control', 'public, max-age=60')
              .setHeader('ETag', eTag)
              .status(200)
              .json(result)
          }
          break
        default:
          res.status(405).json('Method Not Allowed')
      }
    } catch (e) {
      if (e instanceof UnauthenticatedError) {
        res.status(401).json('Unauthorized')
      } else if (e instanceof ZodError) {
        res.status(400).json('Bad request')
      } else if (e instanceof QuotaExceededError) {
        res.status(429).json('Quota exceeded')
      } else {
        res.status(500).json('Internal Server Error')
      }
    } finally {
      res.end()
    }
  },
)
