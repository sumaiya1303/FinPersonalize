import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyBSEUggv6XeDSCkhP07lOjYAw-fGunKF8I",
    authDomain: "fin-ai-twin.firebaseapp.com",
    projectId: "fin-ai-twin",
    storageBucket: "fin-ai-twin.firebasestorage.app",
    messagingSenderId: "581754195120",
    appId: "1:581754195120:web:13949b5e095fbde078ff75"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
