# QAG (Question-Answer Generation Platform)

QAG is a Flet application that helps instructors generate exam questions from text or PDF content. It integrates Firebase for auth/storage, OpenAI for question generation, and Twilio Verify for signup verification.

## Highlights
- Light/dark theme toggle
- Firebase Auth + Firestore + Storage
- PDF/DOCX generation with upload to Firebase Storage
- OpenAI-powered question generation
- Twilio Verify for email/WhatsApp verification during signup

## Requirements
- Python 3.12+ (recommended)
- Firebase project with a service account
- OpenAI API key
- Twilio Verify credentials (required for signup verification)

## Quick Start
1. Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Configure environment variables
Create a `.env` file in the project root.

```env
# Firebase client config
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_STORAGE_BUCKET=
FIREBASE_MESSAGING_SENDER_ID=
FIREBASE_APP_ID=
FIREBASE_MEASUREMENT_ID=
FIREBASE_DATABASE_URL=

# Firebase admin service account
FIREBASE_TYPE=service_account
FIREBASE_PRIVATE_KEY_ID=
FIREBASE_PRIVATE_KEY=
FIREBASE_CLIENT_EMAIL=
FIREBASE_CLIENT_ID=
FIREBASE_AUTH_URI=
FIREBASE_TOKEN_URI=
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=
FIREBASE_CLIENT_X509_CERT_URL=
FIREBASE_UNIVERSE_DOMAIN=googleapis.com

# OpenAI
OPENAI_API_KEY=

# Twilio Verify
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_VERIFY_SID=
```

Notes:
- `FIREBASE_PRIVATE_KEY` must keep literal `\n` line breaks (not real newlines).
- `.env` is already in `.gitignore` and should never be committed.

4. Run the app
```powershell
python main.py
```

## Usage
- Sign up with phone/email verification (Twilio Verify).
- Sign in to access the home view.
- Upload a PDF or paste text, choose question types and model, then generate.
- Generated files are uploaded to Firebase Storage.

## Theme
Use the app bar toggle to switch between light and dark mode. Buttons and key UI elements respond to theme changes.

## Project Structure
- `main.py` - app entrypoint
- `viewscol.py` - route/view handling + app bar actions
- `Views/` - UI views (home, signin, signup)
- `UI/` - shared widgets/utilities
- `Generator/` - PDF/DOCX generation
- `firebaseConfig.py` - Firebase initialization

## Security
- Never commit secrets to git.
- Rotate keys if they were ever exposed in the repo history.
- Prefer environment variables over hardcoded tokens.

## Troubleshooting
### `ModuleNotFoundError: No module named 'pkg_resources'`
Pin setuptools below 82:
```powershell
python -m pip install --force-reinstall "setuptools<82"
```

### `Client.__init__() got an unexpected keyword argument 'proxies'`
Pin httpx below 0.28 (already in `requirements.txt`):
```powershell
python -m pip install -r requirements.txt
```

## License
Nezer@2026
