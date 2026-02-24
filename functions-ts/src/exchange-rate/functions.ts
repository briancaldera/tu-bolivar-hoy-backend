import * as logger from 'firebase-functions/logger'
import * as cheerio from 'cheerio'
import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { Database } from '../../generated/database.types'
import {
  Currency,
  CurrencyValues,
  ExchangeRate,
} from './domain/models/exchange-rate'
import { getCustomAgent } from './utils/custom-fetch'
import fetch from 'node-fetch'
import { z } from 'zod'
import { compareDesc, isBefore } from 'date-fns'
import { IntegrityService } from './application/integrity-service'

const TARGET_URL = 'https://www.bcv.org.ve/'

const selectors: Record<Currency, string> = {
  USD: '#dolar > div > div > div.col-sm-6.col-xs-6.centrado > strong',
  EUR: '#euro > div > div > div.col-sm-6.col-xs-6.centrado > strong',
  RUB: '#rublo > div > div > div.col-sm-6.col-xs-6.centrado > strong',
  TRY: '#lira > div > div > div.col-sm-6.col-xs-6.centrado > strong',
  CNY: '#yuan > div > div > div.col-sm-6.col-xs-6.centrado > strong',
}

export async function fetchExchangeRates(): Promise<void> {
  try {
    const agent = await getCustomAgent()

    const res = await fetch(TARGET_URL, {
      agent: agent,
    })

    const html = await res.text()

    const $ = cheerio.load(html)

    const rates: Record<string, number> = {}

    for (const [currency, selector] of Object.entries(selectors)) {
      const rateString = $(selector).first().text()

      rates[currency] = currencyStringToNumber(rateString)
    }

    logger.info(`Currency ${JSON.stringify(rates)}`)
    await saveExchangeRates(rates)
  } catch (e) {
    const now = new Date()

    if (now.getMinutes() >= 30) {
      logger.error(e)
      await errorCondition()
    } else {
      throw e
    }
  }
}

async function errorCondition(): Promise<void> {
  const supabaseClient = createSupabaseClient()

  const { data } = await supabaseClient
    .from('exchange_rates')
    .select('*')
    .limit(5)
    .order('registered_at', { ascending: false })
    .in('currency', CurrencyValues)

  if (!data) throw Error('ExchangeRates not found')

  for (const currency of CurrencyValues) {
    if (!data.some((rate) => rate.currency === currency)) {
      throw Error(`Exchange rate for currency '${currency}' not found`)
    }
  }

  const previousRates = data.reduce(
    (acc, rate): Record<string, number | null> => {
      return {
        ...acc,
        [rate.currency]: rate.rate,
      }
    },
    {},
  )

  await saveExchangeRates(previousRates)
}

function currencyStringToNumber(rate: string): number {
  const newRate = rate.replace('.', '').replace(',', '.')
  return Number(newRate)
}

async function saveExchangeRates(
  rates: Record<Currency, number | null>,
): Promise<void> {
  const schema = z.record(z.enum(CurrencyValues), z.number())

  const validData = schema.parse(rates)

  const supabaseClient = createSupabaseClient()

  const now = new Date()
  now.setMilliseconds(0)
  now.setSeconds(0)
  now.setMinutes(0)

  const { count } = await supabaseClient
    .from('exchange_rates')
    .select('*', { count: 'exact', head: true })
    .eq('registered_at', now.toISOString())

  if (count && count > 0) {
    logger.warn(`Exchange rates already exist for ${now}`)
    return
  }

  const exchangeRates: ExchangeRate[] = []

  for (const [currency, rate] of Object.entries(validData)) {
    const exchangeRate = ExchangeRate.create(currency, rate, now)
    exchangeRates.push(exchangeRate)
  }

  logger.info('Saving exchange rates...')
  const exchangeRateData = exchangeRates.map((rate) => rate.toJSON())
  const { error } = await supabaseClient
    .schema('private')
    .from('exchange_rates')
    .insert(exchangeRateData)

  if (error) {
    logger.error('Error saving exchange rates...')
    logger.error(error)
  } else {
    logger.info('Exchange rates saved successfully')
  }
}

let client: SupabaseClient<Database>

function createSupabaseClient(): SupabaseClient<Database> {
  const SUPABASE_URL = z.string().nonempty().parse(process.env.SUPABASE_URL)
  const SUPABASE_SECRET_KEY = z
    .string()
    .nonempty()
    .parse(process.env.SUPABASE_SECRET_KEY)

  if (!client) {
    client = createClient<Database>(SUPABASE_URL, SUPABASE_SECRET_KEY, {
      db: {
        schema: 'private',
      },
    })
  }

  return client
}

export async function getExchangeRateForPeriod(
  currency: string,
  hours: [string, string],
) {
  const validCurrency = z.enum(CurrencyValues).parse(currency)
  const validHours = z
    .tuple([z.iso.datetime(), z.iso.datetime()])
    .refine(
      (value) => isBefore(value[0], value[1]),
      'Start date must be before end date',
    )
    .parse(hours)

  const supabaseClient = createSupabaseClient()

  const { data } = await supabaseClient
    .from('exchange_rates')
    .select('*')
    .eq('currency', validCurrency)
    .gte('registered_at', validHours[0])
    .lte('registered_at', validHours[1])
    .throwOnError()

  const data2 = data
    .sort((a, b) => {
      if (!a.registered_at || !b.registered_at) {
        return 0
      }

      return compareDesc(new Date(a.registered_at), new Date(b.registered_at))
    })
    .map((rate) => {
      const { currency, id, ...payload } = rate

      return payload
    })

  if (!hasRateAndDatetime(data2)) {
    throw new Error('There are rates without datetime or rate')
  }

  const map = new Map<number, string[]>()

  data2.forEach((rate) => {
    const set = map.get(rate.rate)

    if (!set) {
      map.set(rate.rate, [rate.registered_at])
    } else {
      map.set(rate.rate, [...set, rate.registered_at])
    }
  })

  return map
}

function hasRateAndDatetime(
  data: { rate: number | null; registered_at: string | null }[],
): data is {
  rate: number
  registered_at: string
}[] {
  return data.every((rate) => rate.rate && rate.registered_at)
}

export async function checkIntegrity() {
  const db = createSupabaseClient()
  const integrityService = new IntegrityService(db)
  await integrityService.checkIntegrity()
}
