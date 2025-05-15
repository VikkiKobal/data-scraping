import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

def find_element_safe(driver_or_elem, selector, by=By.CSS_SELECTOR):
    try:
        return driver_or_elem.find_element(by, selector)
    except:
        return None

def find_elements_safe(driver_or_elem, selector, by=By.CSS_SELECTOR):
    try:
        return driver_or_elem.find_elements(by, selector)
    except:
        return []

def extract_price(offer):
    price_elem = find_element_safe(offer, "td.model-shop-price")
    if price_elem:
        return price_elem.text.strip().replace("\xa0", "").replace("грн", "").strip()
    return "Невідомо"

def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)  

def click_next_page():
    next_button = find_element_safe(driver, "button.list-more-btn")
    if next_button and "disabled" not in next_button.get_attribute("class"):
        next_button.click()
        sleep(2)  
        return True
    return False

driver.get("https://ek.ua/ua/")
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.mainmenu")))

sport = find_element_safe(driver, "body > div.mainmenu > div > ul > li:nth-child(13) > a")
if sport:
    sport.click()
else:
    print("Нема 'Спорт'")
    driver.quit()

bike = find_element_safe(driver, "body > div.mainmenu > div > ul > li:nth-child(13) > div > div > a:nth-child(1)")
if bike:
    bike.click()
else:
    print("Нема 'Велосипеди'")
    driver.quit()

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sub-katalogs")))

subcategory = find_element_safe(driver, "div.sub-katalogs div:nth-child(1) a")
if subcategory:
    subcategory.click()
else:
    print("Не знайдено підкатегорію")
    driver.quit()

all_bikes = []

for page in range(0, 47): 
    url = f"https://ek.ua/ua/ek-list.php?katalog_=161&page_={page}&preset_mode_=0"
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.model-short-div")))

    scroll_to_bottom()

    products = find_elements_safe(driver, "div.model-short-div")

    for product in products:
        model_elem = find_element_safe(product, "span.u")
        model = model_elem.text.strip() if model_elem else "Невідомо"

        link_elem = find_element_safe(product, "a.model-short-title")
        model_url = link_elem.get_attribute("href") if link_elem else None

        img = "Невідомо"
        if model_url:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(model_url)

            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item-img-div div[onclick]")))
                img_elem = find_element_safe(driver, "div.item-img-div div[onclick]")
                if img_elem:
                    onclick_attr = img_elem.get_attribute("onclick")
                    match = re.search(r"window\.id_good\s*=\s*(\d+);", onclick_attr)
                    if match:
                        img_id = match.group(1)
                        img = f"https://s.ek.ua/jpg/{img_id}.jpg"
            except:
                img = "Немає зображення"

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        offers = find_elements_safe(product, "table.model-hot-prices tbody tr")
        for offer in offers[:7]:
            shop_city_elem = find_element_safe(offer, "td:nth-child(1) div a")
            shop_city_text = shop_city_elem.text.replace("→", "").strip() if shop_city_elem else "Невідомо"

            shop_match = re.match(r"^(.*?)\s*\((.*?)\)$", shop_city_text)
            if shop_match:
                shop = shop_match.group(1).strip()
                city = shop_match.group(2).strip() 
            else:
                shop = shop_city_text
                city = "Невідомо"

            price = extract_price(offer)

            all_bikes.append([model, img, shop, city, price])

    print(f" Всього пропозицій: {len(all_bikes)}")

with open("bikes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Модель", "Зображення", "Магазин", "Місто", "Ціна"])
    writer.writerows(all_bikes)

print(f"Усього зібрано: {len(all_bikes)} пропозицій.")
driver.quit()
