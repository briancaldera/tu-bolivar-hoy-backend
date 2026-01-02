import {initializeApp, getApp, FirebaseApp} from 'firebase/app'

let app: FirebaseApp
try {
    app = getApp();
} catch (error) {
    app = initializeApp({
        storageBucket: 'tubolivarhoy.firebasestorage.app'
    });
}

export const firebaseApp: FirebaseApp = app
