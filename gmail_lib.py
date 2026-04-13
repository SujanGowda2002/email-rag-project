import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Handles OAuth2 authentication and returns the Gmail service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def fetch_emails(max_results=10):
    """The REAL function that talks to Google"""
    service = get_gmail_service() 
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    email_data = []
    for msg in messages:
        m = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = m.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        snippet = m.get('snippet', '')
        
        email_data.append({
            "id": msg['id'],
            "subject": subject,
            "content": snippet
        })
    return email_data

def fetch_emails_mock(max_results=10):
    """Return a list of mock emails for testing (Keep this if you want to swap back later)."""
    mock_emails = [
        {"id": "1", "subject": "Project Launch Update", "content": "The project launch is scheduled for next Monday."},
        # ... you can keep the rest of your mock list here if you like
    ]
    return mock_emails[:max_results]