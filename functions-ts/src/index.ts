/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import {initializeApp} from 'firebase-admin/app'
import {onSchedule} from 'firebase-functions/scheduler'
import {fetchExchangeRates, getExchangeRateForPeriod} from './exchange-rate/functions'
import {onCall} from 'firebase-functions/https'

initializeApp({
    storageBucket: 'tubolivarhoy.firebasestorage.app'
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

export const fetchExchangeRateForPeriod = onCall({
    maxInstances: 3,
    timeoutSeconds: 2 * 60
}, async (request, _response) => {
    const currency = request.data.currency
    const startTime = request.data.startDatetime
    const endTime = request.data.endDateTime

    const res = await getExchangeRateForPeriod(currency, [startTime, endTime])

    return {"exchange_rate_map": Object.fromEntries(res)}
})


