from requests import get
from bs4 import BeautifulSoup
import re

BASE_URL = "https://uk.wikipedia.org"
URL = f"{BASE_URL}/wiki/Список_країн"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Отримуємо HTML сторінки
page = get(URL, headers=HEADERS)
soup = BeautifulSoup(page.content, "html.parser")
table = soup.find("table", class_="wikitable")

# Відкриваємо файли для запису
with open("countries_list.txt", "w", encoding="utf-8") as list_file, \
        open("countries_and_languages.txt", "w", encoding="utf-8") as languages_file:
    # Витягуємо країни
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        country_link_tag = cells[1].find("a")
        if country_link_tag:
            country_name = country_link_tag.text.strip()
            country_url = BASE_URL + country_link_tag.get("href")

            # Записуємо країну та її лінк в окремий файл
            list_file.write(f"Країна: {country_name} — {country_url}\n")

            # Виводимо на екран для перевірки
            print(f"Країна: {country_name} — {country_url}")

            # Отримуємо інформацію про країну
            country_info = f"Країна: {country_name} — "
            info_url = BASE_URL + country_link_tag.get("href")
            page_info = get(info_url, headers=HEADERS)
            soup_info = BeautifulSoup(page_info.content, "html.parser")

            # Шукаємо таблицю з офіційними мовами
            infobox = soup_info.find("table", class_="infobox geography")

            # Збираємо мови, видаляючи непотрібні символи та посилання
            official_languages = ""
            if infobox:
                rows = infobox.find_all("tr")
                for row in rows:
                    header = row.find("th")
                    data = row.find("td")
                    if header and data:
                        header_text = header.get_text(strip=True)
                        data_text = data.get_text(strip=True)

                        # Якщо заголовок містить "Офіційні мови"
                        if "Офіційні мови" in header_text:
                            official_languages = re.sub(r"\[.*\]", "", data_text).strip()
                            break  # Перериваємо цикл після знаходження мов

            # Записуємо країну та її офіційні мови в файл
            country_info += official_languages
            languages_file.write(country_info + "\n")
