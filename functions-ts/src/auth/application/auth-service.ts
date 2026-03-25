import { SupabaseClient } from '@supabase/supabase-js'
import { Database } from '@/../../generated/database.types'
import { UnauthenticatedError } from '../errors/unauthenticated-error'
import { z } from 'zod'
import { createHash } from 'node:crypto'
import { assertPresent } from 'ts-extras'
import { QuotaExceededError } from '../../exchange-rate/errors/quota-exceeded-error'
import { Request } from 'firebase-functions/https'

export class AuthService {
  constructor(private readonly database: SupabaseClient<Database>) {}

  async processRequest(request: Request) {
    const keyHeader = request.header('x-api-key')

    if (!keyHeader) throw new UnauthenticatedError()

    const apiKey = z.string().nonempty().parse(keyHeader)

    const secret = apiKey.replace('tbh_key_', '')

    const hashedApiKey = createHash('sha256').update(secret).digest('hex')

    const now = new Date().toISOString()

    const { data: apiKeyObject, error } = await this.database
      .schema('private')
      .from('api_key')
      .select('*')
      .eq('key', hashedApiKey)
      .is('revoked_at', null)
      .or(`expires_at.is.null,expires_at.gt.${now}`)
      .maybeSingle()

    if (error) throw error

    if (!apiKeyObject) {
      console.warn('Invalid API key received')
      throw new UnauthenticatedError()
    }

    console.log('Request with valid API key received')

    // Fire and forget (or use a background task)
    this.database
      .schema('private')
      .from('api_key')
      .update({ last_used_at: now })
      .eq('id', apiKeyObject.id)
      .then()

    const userId = apiKeyObject.owner_id

    const { data: quotaSummary, error: error2 } = await this.database
      .from('user_quota_summary')
      .select('*')
      .eq('user_id', userId)
      .single()

    if (error2) throw error2

    const usage = quotaSummary.usage
    assertPresent(usage)
    const quota = quotaSummary.quota
    assertPresent(quota)

    if (usage >= quota) throw new QuotaExceededError()

    // request does not exceed quota
    const {} = await this.database
      .from('quota_usage')
      .update({ usage: usage + 1 })
      .eq('user_id', userId)
  }
}
