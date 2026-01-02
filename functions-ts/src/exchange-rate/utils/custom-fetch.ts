import {Agent} from 'https'
import * as FirebaseStorage from 'firebase/storage'
import {firebaseApp} from '../app'

const caFile = 'gs://tubolivarhoy.firebasestorage.app/public/assets/ca/bcv.crt'

export async function getCustomAgent(): Promise<Agent> {
    const storage = FirebaseStorage.getStorage(firebaseApp)
    const ref = FirebaseStorage.ref(storage, caFile)

    const fileBytes = await FirebaseStorage.getBytes(ref)

    const decoder = Buffer.from(fileBytes)
    const ca = decoder.toString('utf-8')

    return new Agent({ca: ca})
}

