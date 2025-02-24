from requests import get
from bs4 import BeautifulSoup
import re

BASE_URL = "https://uk.wikipedia.org"
URL = f"{BASE_URL}/wiki/Список_країн"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

FILE_NAME = "countries_and_languages.txt"
with open(FILE_NAME, "w", encoding="utf-8") as file:
    page = get(URL, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table", class_="wikitable")

    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        country_link_tag = cells[1].find("a")

        if country_link_tag:
            country_name = country_link_tag.text.strip()
            country_url = BASE_URL + country_link_tag.get("href")

            file.write(f"Країна: {country_name} — {country_url}\n")
            print(f"Країна: {country_name} — {country_url}")

            country_info = f"Країна: {country_name} — "
            page_info = get(country_url, headers=HEADERS)
            soup_info = BeautifulSoup(page_info.content, "html.parser")

            infobox = soup_info.find("table", class_="infobox geography")

            official_languages = "Немає даних"
            if infobox:
                rows = infobox.find_all("tr")
                for row in rows:
                    header = row.find("th")
                    data = row.find("td")
                    if header and data:
                        header_text = header.get_text(strip=True)
                        data_text = data.get_text(strip=True)

                        if "Офіційні мови" in header_text:
                            official_languages = data_text
                            break

            official_languages = official_languages.replace('і ', ' і').replace(' ,', ',').replace(' , ', ', ')

            official_languages = re.sub(r'\d+', '', official_languages) 
            official_languages = re.sub(r'\[.*?\]', '', official_languages)

            country_info += official_languages
            file.write(f"{country_info}\n")

            print(f"{country_info}\n")

            file.write("\n")
