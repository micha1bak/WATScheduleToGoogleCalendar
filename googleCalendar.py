import datetime
import os.path
import os

from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Daj uprawnienia zapis-odczyt
SCOPES = ["https://www.googleapis.com/auth/calendar"]

"""
Klasa-wrapper do obsługi Google Calendar API.
Zarządza autentykacją i dodawaniem wydarzeń.
"""
class GoogleCalendar:

    creds_file: str
    creds: Credentials
    token_file: Optional[str]
    calendar_id: str
    service: Resource


    def __init__(self, calendar_id: str = "primary") -> None:
        """
        Inicjalizuje serwis API.

        :param calendar_id: ID kalendarza do użycia. "primary" to kalendarz główny.
        """
        load_dotenv()

        # Pobieramy ścieżki z .env lub używamy domyślnych
        self.creds_file = os.environ.get("CREDENTIALS_FILE", "credentials.json")
        if not self.creds_file:
            raise EnvironmentError("CREDENTIALS_FILE environment variable not set and doesn't exist in working directory")
        self.token_file = os.environ.get("TOKEN_FILE", "token.json")
        self.calendar_id: str = os.environ.get("CALENDAR_ID", calendar_id)

        # Autentykacja i budowanie serwisu
        # self.service będzie obiektem, przez który wywołujemy API
        self.service = self._authenticate()

    def _authenticate(self) -> Resource:
        """
        Zarządza procesem logowania OAuth 2.0 i zwraca gotowy obiekt 'service'.
        """
        creds: Credentials | None = None

        # Plik token.json przechowuje tokeny użytkownika.
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        # Jeśli nie ma poprawnych danych logowania, poproś użytkownika o zalogowanie.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Błąd odświeżania tokenu (być może cofnięto zgodę): {e}")
                    # Jeśli odświeżenie się nie uda, usuń stary token i zaloguj od nowa
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    print("Usunięto stary token. Proszę uruchomić skrypt ponownie, aby się zalogować.")
                    exit(1)  # Zakończ, aby użytkownik mógł uruchomić ponownie
            else:
                if not os.path.exists(self.creds_file):
                    print(f"KRYTYCZNY BŁĄD: Nie znaleziono pliku '{self.creds_file}'.")
                    print("Pobierz plik credentials.json z Google Cloud Console.")
                    exit(1)

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Zapisz dane logowania na następny raz
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())

        try:
            service = build("calendar", "v3", credentials=creds)
            print("Pomyślnie połączono z Google Calendar API.")
            return service
        except HttpError as error:
            print(f"Wystąpił błąd podczas budowania serwisu API: {error}")
            exit(1)

    def _convert_lesson_to_times(self, lesson_data: Dict[str, Any]) -> Dict[str, str] | None:
        """
        PRYWATNA METODA POMOCNICZA

        Konwertuje słownik danych lekcji (z datą i ID bloku) na konkretne
        daty i godziny rozpoczęcia/zakończenia w formacie ISO.

        :param lesson_data: Słownik danych ze scrapera
        :return: Słownik {"start_iso": "...", "end_iso": "..."} lub None
        """

        date_str = lesson_data.get("date")  # np. "2025_10_01"
        block_id = lesson_data.get("block_id")  # np. "block6"

        if not date_str or not block_id:
            print(f"Ostrzeżenie: Brak 'date' lub 'block_id' w danych: {lesson_data}. Pomijam.")
            return None

        # Stwórz mapowanie: block_id -> (godzina_start, godzina_koniec)
        time_mapping = {
            "block1": ("08:00:00", "09:35:00"),
            "block2": ("09:50:00", "11:25:00"),
            "block3": ("11:40:00", "13:15:00"),
            "block4": ("13:30:00", "15:05:00"),
            "block5": ("16:00:00", "17:35:00"),
            "block6": ("17:50:00", "19:25:00"),
            "block7": ("19:40:00", "21:15:00"),
        }

        times = time_mapping.get(block_id)
        if not times:
            print(f"Ostrzeżenie: Nieznany block_id: {block_id}. Pomijam.")
            return None

        date_iso = date_str.replace("_", "-")  # "2025-10-01"
        start_time_iso = f"{date_iso}T{times[0]}"
        end_time_iso = f"{date_iso}T{times[1]}"

        return {"start_iso": start_time_iso, "end_iso": end_time_iso}

    def add_lesson_to_calendar(self, lesson_data: Dict[str, Any]):
        """
        Przyjmuje słownik danych lekcji i dodaje go jako wydarzenie.

        :param lesson_data: Słownik ze scrapera, np.:
            {
                "date": "2026_03_05",
                "block_id": "block6",
                "name": "F2 (Inne) 313 S [6]",
                "info": "Fizyka 2 - (Egzamin poprawkowy) -",
                "color": "#E9967A"
            }
        """

        # 1. Konwertuj dane lekcji na czasy start/end
        times = self._convert_lesson_to_times(lesson_data)
        if not times:
            return  # Pomiń, jeśli konwersja się nie udała (np. zły block_id)

        # 2. Stwórz "ciało" wydarzenia (event body)
        event_body = {
            "summary": lesson_data.get("info", "Brak tytułu"),
            "description": lesson_data.get("name", "Brak opisu"),
            # 'location': '...', # TODO: Wyciągnąć nr sali z 'name'
            "start": {
                "dateTime": times["start_iso"],
                "timeZone": "Europe/Warsaw",
            },
            "end": {
                "dateTime": times["end_iso"],
                "timeZone": "Europe/Warsaw",
            },
            # TODO: Mapować 'color' na 'colorId' Google
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 15},
                ],
            },
        }

        # 3. Wyślij zapytanie do API
        try:
            event = self.service.events().insert(calendarId=self.calendar_id, body=event_body).execute()

            print(f"Utworzono wydarzenie: {event.get('summary')} ({event.get('htmlLink')})")
        except HttpError as error:
            print(f"Wystąpił błąd podczas dodawania wydarzenia {lesson_data.get('info')}: {error}")

    def list_next_events(self, count: int = 10):
        """
        Wypisuje nadchodzące wydarzenia (dla celów testowych).
        """
        try:
            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            print(f"Pobieram {count} nadchodzących wydarzeń...")
            events_result = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=now,
                    maxResults=count,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                print("Nie znaleziono nadchodzących wydarzeń.")
                return

            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])

        except HttpError as error:
            print(f"Wystąpił błąd podczas pobierania wydarzeń: {error}")