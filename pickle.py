import datetime
import os.path
import pickle
import requests
import speech_recognition as sr
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.cloud import translate
import matplotlib.pyplot as plt

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/tasks.readonly']

def get_credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_calendar_events(creds):
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def get_tasks(creds):
    service = build('tasks', 'v1', credentials=creds)
    tasks_result = service.tasks().list(tasklist='@default').execute()
    tasks = tasks_result.get('items', [])
    return tasks

def synthesize_speech(text):
    response = requests.post(
        "https://api.eleven-labs.com/v1/speech_synthesis",
        json={"text": text, "voice": "your_preferred_voice"}
    )

    if response.status_code == 200:
        with open("output_audio.wav", "wb") as audio_file:
            audio_file.write(response.content)
        print("Speech synthesis completed. Audio file saved as output_audio.wav")
    else:
        print("Speech synthesis request failed. Status code:", response.status_code)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("Speech Recognized:", text)
            return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service:", str(e))
    return ""

def translate_text(text, target_language):
    translator = translate.TranslationServiceClient()
    parent = translator.location_path("your_project_id", "global")
    response = translator.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "target_language_code": target_language,
        }
    )
    return response.translations[0].translated_text

def plot_data(x_values, y_values, title, x_label, y_label):
    plt.plot(x_values, y_values)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

if __name__ == '__main__':
    credentials = get_credentials()
    calendar_events = get_calendar_events(credentials)
    tasks = get_tasks(credentials)

    # Process and store the data as needed
    # For example, print out the events and tasks
    print('Upcoming Calendar Events:')
    for event in calendar_events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    print('\nTasks:')
    for task in tasks:
        print(task['title'])

    # Synthesize speech based on the fetched data
    speech_text = "You have upcoming events and tasks. Please check your calendar and task list."
    synthesize_speech(speech_text)

    # Recognize speech from the user
    user_speech = recognize_speech()
    if user_speech:
        # Translate the user's speech to a different language
        translated_speech = translate_text(user_speech, "fr")
        print("Translated Speech:", translated_speech)
