import os

import pyrebase
import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
from firebase_admin import auth as adminAuth

load_dotenv()

config = {
  "apiKey": os.getenv("FIREBASE_API_KEY"),
  "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
  "projectId": os.getenv("FIREBASE_PROJECT_ID"),
  "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.getenv("FIREBASE_APP_ID"),
  "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
  "databaseURL": os.getenv("FIREBASE_DATABASE_URL", ""),
}

private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")

certificate = {
  "type": os.getenv("FIREBASE_TYPE", "service_account"),
  "project_id": os.getenv("FIREBASE_PROJECT_ID"),
  "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
  "private_key": private_key,
  "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
  "client_id": os.getenv("FIREBASE_CLIENT_ID"),
  "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
  "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
  "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
  "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
  "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
}

# initialise Firebase authentication
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# initialise Firestore cloud storage
cred = credentials.Certificate(certificate)
firebase_admin.initialize_app(cred,{'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")})
db = firestore.client()
store = storage
