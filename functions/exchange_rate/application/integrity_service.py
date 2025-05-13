from datetime import datetime, timedelta

from firebase_functions import logger

from exchange_rate.adapter.output.database.models.exchange_rate import ExchangeRateAR


class IntegrityService:
    _NUMBER_OF_ROWS = 24 * 5

    def check_integrity(self):
        logger.info("Checking database integrity...")

        failed_days = []

        start_date = datetime(year=2025, month=2, day=20, hour=0, minute=0, second=0)
        current_date = start_date
        now = datetime.now().replace(minute=0, second=0, microsecond=0)

        while current_date < now:
            rows_count = ExchangeRateAR.select().where((ExchangeRateAR.datetime >= current_date) & (ExchangeRateAR.datetime < (current_date + timedelta(hours=24)))).count()
            if rows_count != self._NUMBER_OF_ROWS:
                failed_days.append(current_date)
                logger.error(f"Integrity check failed for {current_date}: expected {self._NUMBER_OF_ROWS} rows, found {rows_count}")

            current_date += timedelta(days=1)

        if failed_days:
            logger.info(f"Integrity check completed. Failed days: {failed_days}")

            for failed_day in failed_days:
                rows = ExchangeRateAR.select().where((ExchangeRateAR.datetime >= failed_day) & (ExchangeRateAR.datetime < (failed_day + timedelta(hours=24))))
                missing_hours = []
                for hour in range(0, 24):
                    if rows.where(ExchangeRateAR.datetime == failed_day.replace(hour=hour)).count() != 5:
                        missing_hours.append(hour)

                logger.error(f"Missing hours for {failed_day}: {missing_hours}")
        else:
            logger.info("Integrity check completed. No issues found.")