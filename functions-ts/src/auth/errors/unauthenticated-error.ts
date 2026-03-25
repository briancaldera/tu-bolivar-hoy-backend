export class UnauthenticatedError extends Error {
  name = 'UnauthenticatedError'
  constructor(message: string = 'Unauthenticated') {
    super(message)
  }
}
