import os
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only scope — the app can only READ emails, never send/delete/modify
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'credentials.json'


def authenticate_gmail():
    """
    Handles the OAuth flow. First run opens a browser window for login/consent.
    Subsequent runs reuse the saved token.json until it expires.
    """
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    "credentials.json not found. Download it from Google Cloud Console "
                    "and place it in the project root."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def extract_body(payload):
    """
    Recursively extracts plain-text body from Gmail's nested payload structure.
    Falls back to empty string if no plain text part is found.
    """
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        # Recurse into nested multipart sections (e.g., multipart/alternative inside multipart/mixed)
        for part in payload['parts']:
            if 'parts' in part:
                result = extract_body(part)
                if result:
                    return result
        # Fallback: try HTML part and strip tags roughly
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html' and 'data' in part.get('body', {}):
                data = part['body']['data']
                html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                return re.sub('<[^<]+?>', ' ', html)
    elif 'data' in payload.get('body', {}):
        data = payload['body']['data']
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    return ""


def get_header(headers, name):
    return next((h['value'] for h in headers if h['name'].lower() == name.lower()), "")


def fetch_recent_emails(service, max_results=10):
    """
    Fetches the most recent emails from the user's inbox and returns a list of
    dicts with subject, sender, date, and body text for each.
    """
    results = service.users().messages().list(
        userId='me', maxResults=max_results, labelIds=['INBOX']
    ).execute()

    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()

        headers = msg_data['payload']['headers']
        subject = get_header(headers, 'Subject')
        sender = get_header(headers, 'From')
        date = get_header(headers, 'Date')

        body = extract_body(msg_data['payload'])
        snippet = msg_data.get('snippet', '')

        # Clean sender to extract just the email address from "Name <email@domain.com>"
        sender_email_match = re.search(r'[\w\.-]+@[\w\.-]+', sender)
        sender_email = sender_email_match.group(0) if sender_email_match else sender

        emails.append({
            "id": msg['id'],
            "subject": subject if subject else "(No subject)",
            "sender_display": sender,
            "sender_email": sender_email,
            "date": date,
            "body": body if body else snippet,
        })

    return emails