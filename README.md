# 🤖 Synchronizator Planu Zajęć z Kalendarzem Google

Prosty skrypt w Pythonie, który automatycznie pobiera plan zajęć ze strony wydziału i dodaje je jako wydarzenia do Kalendarza Google.

## 🚀 Główne funkcje

* Pobiera dane o zajęciach (data, nazwa, sala) ze strony WWW.
* Filtruje zajęcia (np. tylko z wybranego semestru).
* Uwierzytelnia się w Google Calendar API przy użyciu OAuth 2.0.
* Tworzy nowe wydarzenia w kalendarzu.
* (Opcjonalnie: Pomija duplikaty, jeśli już istnieją).

## 🛠️ Wymagania wstępne

* Python 3.7+
* Konto Google
* Włączone Google Calendar API w projekcie Google Cloud Console.

## ⚙️ Instalacja i Konfiguracja

1.  **Klonuj repozytorium:**
    ```bash
    git clone [adres-twojego-repozytorium]
    cd [nazwa-folderu]
    ```

2.  **Utwórz i aktywuj środowisko wirtualne:**
    ```bash
    # Na Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Na Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Zainstaluj zależności:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfiguracja Google API:**
    * W [Google Cloud Console](https://console.cloud.google.com/) włącz **Google Calendar API**.
    * Utwórz dane logowania "Identyfikator klienta OAuth 2.0" dla typu aplikacji "Aplikacja komputerowa".
    * Pobierz plik JSON z kluczami. **Zmień jego nazwę na `credentials.json`** i umieść go w głównym folderze projektu.

5.  **Konfiguracja zmiennych środowiskowych:**
    * Skopiuj plik `.env.example` do nowego pliku `.env`:
        ```bash
        # Na Windows
        copy .env.example .env

        # Na Mac/Linux
        cp .env.example .env
        ```
    * Otwórz plik `.env` i uzupełnij go. Najważniejsza zmienna to `CALENDAR_ID`. Możesz wpisać `primary`, aby używać swojego głównego kalendarza.

## 🏃 Uruchomienie

1.  **Pierwsze uruchomienie (Autoryzacja):**
    ```bash
    python main.py
    ```
    * Skrypt automatycznie otworzy Twoją przeglądarkę.
    * Zaloguj się na konto Google, którego kalendarza chcesz używać.
    * Zaakceptuj prośbę o uprawnienia (do zarządzania kalendarzem).
    * Po pomyślnej autoryzacji skrypt utworzy plik `token.json`.

2.  **Kolejne uruchomienia:**
    Po prostu uruchom skrypt ponownie. Dzięki plikowi `token.json` nie będziesz musiał logować się za każdym razem.
    ```bash
    python main.py
    ```

## ⚠️ Ważne Pliki (Ignorowane przez Git)

Upewnij się, że pliki zawierające Twoje sekrety **nigdy** nie trafią do repozytorium. Plik `.gitignore` w tym projekcie powinien blokować:

* `credentials.json` (Twój "klucz" do aplikacji Google)
* `token.json` (Twój osobisty token logowania)
* `.env` (Twoja lokalna konfiguracja)
* `venv/` (Środowisko wirtualne)

## 🔗 Zasoby
* https://realpython.com/beautiful-soup-web-scraper-python/
* https://www.crummy.com/software/BeautifulSoup/bs4/doc/
* https://developers.google.com/workspace/calendar/api/quickstart/python