import scrapy

class XpathSpider(scrapy.Spider):
    name = 'xpath_spider'
    start_urls = ['https://uk.wikipedia.org/wiki/Список_країн']

    custom_settings = {
        'FEEDS': {
            'countries_xpath.json': {'format': 'json', 'encoding': 'utf8', 'indent': 4},
            'countries_xpath.xml': {'format': 'xml', 'encoding': 'utf8', 'indent': 4},
            'countries_xpath.csv': {'format': 'csv', 'encoding': 'utf8'},
        },
        'FEED_EXPORT_FIELDS': ['Країна', 'URL', 'Столиця', 'Офіційні мови', 'Незалежність', 'Валюта', 'Телефонний код']
    }

    def parse(self, response):
        rows = response.xpath("//table[contains(@class, 'wikitable')]//tr")[1:]

        for row in rows:
            country_name = row.xpath(".//td[2]//a/text()").get()
            country_url = row.xpath(".//td[2]//a/@href").get()

            if country_name and country_url:
                country_url = response.urljoin(country_url)
                yield scrapy.Request(
                    country_url,
                    callback=self.parse_country_info,
                    meta={'country_name': country_name, 'country_url': country_url}
                )

    def parse_country_info(self, response):
        country_name = response.meta['country_name']
        country_url = response.meta['country_url']

        infobox = response.xpath("//table[contains(@class, 'infobox geography')]")
        country_details = {}

        if infobox:
            rows = infobox.xpath(".//tr")
            for row in rows:
                header = row.xpath(".//th//text() | .//th//a/text()").get()
                data = row.xpath(".//td//text() | .//td//a/text()").getall()

                if header and data:
                    header = header.strip()
                    data = ' '.join([d.strip() for d in data if d.strip()]).strip()

                    if "Столиця" in header or "(та найбільше місто)" in header:
                        country_details['Столиця'] = data
                    elif "Офіційні мови" in header:
                        country_details['Офіційні мови'] = data
                    elif "Незалежність" in header:
                        country_details['Незалежність'] = data
                    elif "Валюта" in header:
                        country_details['Валюта'] = data
                    elif "Телефонний код" in header:
                        country_details['Телефонний код'] = data

            # Додаткові перевірки для різних структур таблиці
            if 'Столиця' not in country_details:
                capital = infobox.xpath(".//td[b/a[@title='Столиця']]/following-sibling::td//a/text()").get()
                if not capital:
                    capital = infobox.xpath(".//td[b/a/text()='Столиця']/following-sibling::td//a/text()").get()
                if capital:
                    country_details['Столиця'] = capital.strip()
                else:
                    capital = infobox.xpath(".//td[contains(text(), 'Столиця')]/following-sibling::td//text()").get()
                    if capital:
                        country_details['Столиця'] = capital.strip()

            if 'Столиця' not in country_details:
                country_details['Столиця'] = 'Невідомо'

        yield {
            'Країна': country_name,
            'URL': country_url,
            'Столиця': country_details.get('Столиця', 'Невідомо'),
            'Офіційні мови': country_details.get('Офіційні мови', 'Невідомо'),
            'Незалежність': country_details.get('Незалежність', 'Невідомо'),
            'Валюта': country_details.get('Валюта', 'Невідомо'),
            'Телефонний код': country_details.get('Телефонний код', 'Невідомо')
        }
