import * as logger from 'firebase-functions/logger'
import { addDays, addHours } from 'date-fns'
import { SupabaseClient } from '@supabase/supabase-js'
import { Database } from '../../../generated/database.types'
import { assertPresent } from 'ts-extras'

export class IntegrityService {
  private NUMBER_OF_ROWS = 24 * 5

  constructor(private readonly db: SupabaseClient<Database>) {}

  async checkIntegrity() {
    logger.info('Checking integrity service...')

    const failedDays: Date[] = []

    const startDate = new Date(2025, 2, 20, 0, 0, 0, 0)
    let currentDate = startDate
    const now = new Date()
    now.setMilliseconds(0)
    now.setSeconds(0)
    now.setMinutes(0)
    now.setHours(0)

    while (currentDate < now) {
      const { count: rowsCount } = await this.db
        .schema('private')
        .from('exchange_rates')
        .select('registered_at', { count: 'exact', head: true })
        .gte('registered_at', currentDate.toISOString())
        .lt('registered_at', addHours(currentDate, 24).toISOString())

      assertPresent(rowsCount)

      if (rowsCount !== this.NUMBER_OF_ROWS) {
        failedDays.push(currentDate)
        logger.warn(
          `Integrity check failed for ${currentDate}: expected ${this.NUMBER_OF_ROWS} rows, found ${rowsCount}`,
        )
      }

      currentDate = addDays(currentDate, 1)
    }

    if (failedDays.length > 0) {
      logger.warn(
        `Integrity check completed. Failed days: ${failedDays.join(',')}`,
      )

      for (const failedDay of failedDays) {
        const rows = this.db
          .schema('private')
          .from('exchange_rates')
          .select('registered_at', { count: 'exact', head: true })
          .gte('registered_at', failedDay.toISOString())
          .lt('registered_at', addHours(failedDay, 24).toISOString())

        const missingHours = []

        for (const hour of Array.from({ length: 24 }, (v, t) => t)) {
          failedDay.setHours(hour)

          if (
            (await rows.eq('registered_at', failedDay.toISOString())).count !==
            5
          ) {
            missingHours.push(hour)
          }
        }

        logger.error(
          `Missing hours for ${failedDay}: [${missingHours.join(',')}]`,
        )
      }
    } else {
      logger.info('Integrity check completed. No issues found.')
    }
  }
}
