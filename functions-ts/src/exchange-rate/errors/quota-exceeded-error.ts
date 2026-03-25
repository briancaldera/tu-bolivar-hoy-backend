export class QuotaExceededError extends Error {
  name = 'QuotaExceededError'
  constructor(message: string = 'Quota exceeded') {
    super(message)
  }
}
