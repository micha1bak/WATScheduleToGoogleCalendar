import os
import requests

from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any



class Scraper:

    # 'Optional[str]' oznacza, że typem jest 'str' lub 'None'
    # (bo os.environ.get() zwraca None, jeśli nie znajdzie zmiennej)
    URL: Optional[str]
    START_DATE: Optional[str]
    END_DATE: Optional[str]

    # ResultSet[Any] to typ, który zwraca soup.find_all(...)
    lessons: ResultSet[Any]

    # List[Tag] to lista elementów HTML, które pasują do naszych dat
    lessons_in_sem: List[Tag]

    # 'Dict[str, str]' jest bardziej precyzyjne niż 'dict' (mówimy, że klucze i wartości są stringami)
    blocks: List[Dict[str, str]]

    # Pobiera html i scrapuje bloki lekcyjne
    def __init__(self) -> None:

        load_dotenv()

        self.URL = os.environ.get("URL")
        if not self.URL:
            raise EnvironmentError("URL environment variable not set")

        self.START_DATE = os.environ.get("START_DATE")
        if not self.START_DATE:
            raise EnvironmentError("START_DATE environment variable not set")

        self.END_DATE = os.environ.get("END_DATE")
        if not self.END_DATE:
            raise EnvironmentError("END_DATE environment variable not set")

        page: requests.Response = requests.get(self.URL)
        soup: BeautifulSoup = BeautifulSoup(page.text, "html.parser")

        self.lessons = soup.find_all("div", class_="lesson")
        self.lessons_in_semester = []
        self.blocks = []

    # Filtruje i formatuje bloki zajęciowe
    def getBlocks(self) -> List[Dict[str, str]]:

        # Filtruj lekcje na podstawie daty
        for lesson in self.lessons:

            # 1. Znajdź span z datą wewnątrz elementu 'lesson'
            date_span = lesson.find("span", class_="date")

            # 2. Pomiń elementy, które z jakiegoś powodu nie mają daty
            if not date_span:
                continue

            # 3. Wyciągnij tekst i usuń białe znaki
            #    "  2026_03_05  " -> "2026_03_05"
            date_str = date_span.get_text(strip=True)

            # 4. Porównaj daty (jako stringi)
            if self.START_DATE <= date_str <= self.END_DATE:
                # Jeśli data mieści się w przedziale, dodaj element do nowej listy
                self.lessons_in_semester.append(lesson)

        # Formatuj informacje o bloku zajec
        for lesson in self.lessons_in_semester:

            # 1. Utwórz słownik na informacje o bloku zajeć
            block = {}

            # 2. Wpisz dane do bloku
            block["date"] = lesson.find("span", class_="date").text
            block["block_id"] = lesson.find("span", class_="block_id").text
            block["name"] = lesson.find("span", class_="name").text
            block["info"] = lesson.find("span", class_="info").text
            block["color"] = lesson.find("span", class_="colorp").text

            # 3. Dodaj blok do listy bloków
            self.blocks.append(block)

        return self.blocks