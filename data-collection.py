from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Constants for Google API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/tasks.readonly']
SERVICE_ACCOUNT_FILE = 'path/to/service_account.json'

# Initialize credentials and service
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
calendar_service = build('calendar', 'v3', credentials=credentials)
tasks_service = build('tasks', 'v1', credentials=credentials)

def get_calendar_events():
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = calendar_service.events().list(calendarId='primary', timeMin=now,
                                                   maxResults=10, singleEvents=True,
                                                   orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def get_tasks():
    # Call the Tasks API
    tasks_result = tasks_service.tasks().list(tasklist='@default').execute()
    tasks = tasks_result.get('items', [])
    return tasks

# Example usage
if __name__ == '__main__':
    calendar_events = get_calendar_events()
    tasks = get_tasks()

    # Process and store the data as needed
    # For example, print out the events and tasks
    print('Upcoming Calendar Events:')
    for event in calendar_events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    print('\nTasks:')
    for task in tasks:
        print(task['title'])
