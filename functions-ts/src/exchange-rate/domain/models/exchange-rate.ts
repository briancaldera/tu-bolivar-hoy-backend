import { v7 as uuid7 } from 'uuid'
import { z } from 'zod'

export class ExchangeRate {
  readonly id: string
  readonly currency: Currency
  readonly rate: number | null
  readonly registered_at: Date

  private constructor(
    id: string,
    currency: string,
    rate: number | null,
    registered_at: Date,
  ) {
    this.id = z.string().nonempty().parse(id)
    this.currency = z.enum(CurrencyValues).parse(currency)
    this.rate = rate
    this.registered_at = registered_at
  }

  toJSON() {
    return {
      id: this.id,
      currency: this.currency,
      rate: this.rate,
      registered_at: this.registered_at.toJSON(),
    }
  }

  static fromJSON(
    id: string,
    currency: string,
    rate: number,
    registered_at: string,
  ) {
    return new ExchangeRate(id, currency, rate, new Date(registered_at))
  }

  static create(currency: string, rate: number | null, registered_at: Date) {
    const id = uuid7()
    return new ExchangeRate(id, currency, rate, registered_at)
  }
}

export const CurrencyValues = ['USD', 'EUR', 'RUB', 'TRY', 'CNY'] as const

export type Currency = (typeof CurrencyValues)[number]
