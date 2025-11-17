from scraper import Scraper
from googleCalendar import GoogleCalendar
from dotenv import load_dotenv


def main():
    """Główna funkcja uruchamiająca skrypt."""
    print("--- Start: Synchronizacja planu zajęć ---")

    # 1. Załaduj zmienne (choć google_calendar też to robi, warto tu)
    load_dotenv()

    # 2. Pobierz "surowe" dane ze strony
    scr = Scraper()
    wszystkie_lekcje = scr.get_blocks()

    if not wszystkie_lekcje:
        print("Nie znaleziono żadnych lekcji. Kończę pracę.")
        return

    # 5. TODO: Logika sprawdzania duplikatów
    # (Pobierz istniejące wydarzenia, żeby nie dodać ich drugi raz)

    # 6. Dodaj przefiltrowane lekcje do kalendarza
    print("Dodaję wydarzenia do kalendarza...")
    google_cal = GoogleCalendar()
    for lekcja in wszystkie_lekcje:
        google_cal.add_lesson_to_calendar(lekcja)

    print("--- Koniec: Synchronizacja zakończona ---")


if __name__ == "__main__":
    main()