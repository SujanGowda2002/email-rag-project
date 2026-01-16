def fetch_emails_mock(max_results=10):
    """Return a list of mock emails for testing."""
    mock_emails = [
        {"id": "1", "subject": "Project Launch Update", "content": "The project launch is scheduled for next Monday."},
        {"id": "2", "subject": "Meeting Reminder", "content": "Don't forget our team meeting tomorrow at 10 AM."},
        {"id": "3", "subject": "Budget Approval", "content": "The budget for Q1 has been approved by management."},
        {"id": "4", "subject": "Client Feedback", "content": "Client feedback on the latest release is positive."},
        {"id": "5", "subject": "New Hire Onboarding", "content": "Please welcome the new team member starting next week."},
        {"id": "6", "subject": "Server Maintenance", "content": "Server maintenance will occur this Friday at 11 PM."},
        {"id": "7", "subject": "Marketing Campaign", "content": "The new marketing campaign launch is scheduled for Tuesday."},
        {"id": "8", "subject": "Team Outing", "content": "Our quarterly team outing is planned for next month."},
        {"id": "9", "subject": "Policy Update", "content": "Updated company policies have been shared on the intranet."},
        {"id": "10", "subject": "Security Alert", "content": "Please reset your password to comply with new security policies."},
    ]
    return mock_emails[:max_results]