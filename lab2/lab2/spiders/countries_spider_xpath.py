import scrapy

class XpathSpider(scrapy.Spider):
    name = 'xpath_spider'
    start_urls = ['https://uk.wikipedia.org/wiki/Список_країн']

    custom_settings = {
        'FEEDS': {
            'countries_xpath.json': {'format': 'json', 'encoding': 'utf8', 'indent': 4},
            'countries_xpath.xml': {'format': 'xml', 'encoding': 'utf8', 'indent': 4},
            'countries_xpath.csv': {'format': 'csv', 'encoding': 'utf8'},
        }
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
        country_details = {}
        infobox = response.xpath("//table[contains(@class, 'infobox geography')]")

        if infobox:
            rows = infobox.xpath(".//tr")
            for row in rows:
                header = row.xpath(".//th//text() | .//th//a/text()").get()
                data = row.xpath(".//td//text() | .//td//a/text()").getall()

                if header and data:
                    header = header.strip()
                    data = ' '.join([d.strip() for d in data if d.strip()]).strip()
                    country_details[header] = data

        yield country_details
