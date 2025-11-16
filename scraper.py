import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

URL = os.environ.get("URL")
START_DATE = os.environ.get("START_DATE")
END_DATE = os.environ.get("END_DATE")
page = requests.get(URL)
soup = BeautifulSoup(page.text, "html.parser")
lessons = soup.find_all("div", class_="lesson")
lessons_in_sem = []
blocks = []



# Filtruj lekcje na podstawie daty
for lesson in lessons:

    # 1. Znajdź span z datą wewnątrz elementu 'lesson'
    date_span = lesson.find("span", class_="date")

    # 2. Pomiń elementy, które z jakiegoś powodu nie mają daty
    if not date_span:
        continue

    # 3. Wyciągnij tekst i usuń białe znaki
    #    "  2026_03_05  " -> "2026_03_05"
    date_str = date_span.get_text(strip=True)

    # 4. Porównaj daty (jako stringi)
    if START_DATE <= date_str <= END_DATE:
        # Jeśli data mieści się w przedziale, dodaj element do nowej listy
        lessons_in_sem.append(lesson)


# Formatuj informacje o bloku zajec
for lesson in lessons_in_sem:

    # 1. Utwórz słownik na informacje o bloku zajeć
    block = {}

    # 2. Wpisz dane do bloku
    block["date"] = lesson.find("span", class_="date").text
    block["block_id"] = lesson.find("span", class_="block_id").text[5]
    block["name"] = lesson.find("span", class_="name").text
    block["info"] = lesson.find("span", class_="info").text
    block["color"] = lesson.find("span", class_="colorp").text

    # 3. Dodaj blok do listy bloków
    blocks.append(block)
