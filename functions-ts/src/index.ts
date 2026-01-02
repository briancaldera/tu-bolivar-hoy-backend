/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import { onSchedule } from 'firebase-functions/scheduler'
import { fetchExchangeRates } from '@/exchange-rate/functions'

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
