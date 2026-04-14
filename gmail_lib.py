import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope:
# readonly means this app can only read emails, not send/delete/modify them.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """
    Handle Gmail OAuth2 authentication and return a Gmail API service object.

    Workflow:
    - If token.json exists, reuse saved credentials
    - If credentials are expired, refresh them
    - Otherwise, open browser login flow using credentials.json
    """
    creds = None

    # Load previously saved user token if available
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no valid credentials, refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the expired token silently
            creds.refresh(Request())
        else:
            # Start a new login flow in the browser
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the token locally for future runs
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Build and return the Gmail API client
    return build("gmail", "v1", credentials=creds)


def fetch_emails(max_results=10):
    """
    Fetch recent emails from the user's Gmail inbox.

    Args:
        max_results (int): Maximum number of emails to fetch.

    Returns:
        list: A list of dictionaries containing:
              - id
              - subject
              - date
              - content (snippet)
    """
    service = get_gmail_service()

    # Get a list of recent message IDs
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    email_data = []

    # Fetch full metadata for each message
    for msg in messages:
        m = service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        headers = m.get("payload", {}).get("headers", [])

        # Extract useful fields from email headers
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"),
            "No Subject"
        )
        date = next(
            (h["value"] for h in headers if h["name"] == "Date"),
            "Unknown Date"
        )

        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

        # Gmail snippet is a short preview of the email body
        snippet = m.get("snippet", "")

        email_data.append({
            "id": msg["id"],
            "subject": subject,
            "date": date,
            "from": sender,
            "content": snippet
        })

    return email_data


def fetch_emails_mock(max_results=10):
    """
    Return mock emails for testing without connecting to Gmail.

    Useful when:
    - Gmail API is not set up yet
    - you want predictable test data
    - you want to debug the RAG pipeline only
    """
    mock_emails = [
        {
            "id": "1",
            "subject": "Project Launch Update",
            "content": "The project launch is scheduled for next Monday."
        },
        # Add more sample emails here if needed
    ]

    return mock_emails[:max_results]