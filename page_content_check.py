from requests import get


URL = "https://uk.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BA%D1%80%D0%B0%D1%97%D0%BD_%D1%81%D0%B2%D1%96%D1%82%D1%83"
page = get(URL)

print (page.text)