import { Database } from '@/../../generated/database.types'
import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { z } from 'zod'

let client: SupabaseClient<Database>

export function createAdminSupabaseClient(): SupabaseClient<Database> {
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
