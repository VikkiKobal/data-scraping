import scrapy


class CssSpider(scrapy.Spider):
    name = 'css_spider'
    start_urls = ['https://uk.wikipedia.org/wiki/Список_країн']

    custom_settings = {
        'FEEDS': {
            'countries_css.json': {'format': 'json', 'encoding': 'utf8', 'indent': 4},
            'countries_css.xml': {'format': 'xml', 'encoding': 'utf8', 'indent': 4},
            'countries_css.csv': {'format': 'csv', 'encoding': 'utf8'},
        },
        'FEED_EXPORT_FIELDS': ['Країна', 'URL', 'Столиця', 'Офіційні мови', 'Незалежність', 'Валюта', 'Телефонний код']
    }

    def parse(self, response):
        rows = response.css('table.wikitable tbody tr')[1:]  

        for row in rows:
            country_name = row.css('td:nth-child(2) a::text').get()
            country_url = row.css('td:nth-child(2) a::attr(href)').get()

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

        infobox = response.css('table.infobox.geography')
        country_details = {}

        if infobox:
            rows = infobox.css('tr')

            for row in rows:
                header = row.css('th *::text').get()  
                data = row.css('td *::text').getall()  

                if header and data:
                    header = header.strip()
                    data = ' '.join([d.strip() for d in data if d.strip()]).strip()

                    if 'Столиця' in header:
                        country_details['Столиця'] = data
                    elif 'Офіційні мови' in header:
                        country_details['Офіційні мови'] = data
                    elif 'Незалежність' in header:
                        country_details['Незалежність'] = data
                    elif 'Валюта' in header:
                        country_details['Валюта'] = data
                    elif 'Телефонний код' in header:
                        country_details['Телефонний код'] = data

        yield {
            'Країна': country_name,
            'URL': country_url,
            'Столиця': country_details.get('Столиця', 'Невідомо'),
            'Офіційні мови': country_details.get('Офіційні мови', 'Невідомо'),
            'Незалежність': country_details.get('Незалежність', 'Невідомо'),
            'Валюта': country_details.get('Валюта', 'Невідомо'),
            'Телефонний код': country_details.get('Телефонний код', 'Невідомо')
        }
