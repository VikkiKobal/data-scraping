import os
import re
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
import pyodbc


class CapitalCleanupPipeline:
    def clean_capital(self, capital):
        """Функція повного очищення столиці від зайвих символів, чисел і залишків."""
        cleaned_capital = re.sub(
            r'\d+°?|\d+[′″]?|\b[пнсхз]\.\b|\b[шд]\.\b|зх\.|сх\.|пн\.|пд\.|′|″|\bш\.|\bд\.|\b\d+\b',
            '',
            capital
        )
        cleaned_capital = re.sub(r'\s*′\s*′', '', cleaned_capital)

        cleaned_capital = re.sub(
            r'\s+country\s+[A-Z](?:\s+[A-Z])*',
            '',
            cleaned_capital
        )

        cleaned_capital = ' '.join(cleaned_capital.split())
        
        return cleaned_capital.strip()

    def process_item(self, item, spider):
        """Обробка кожного item'а для очищення столиці."""
        if 'Столиця' in item and isinstance(item['Столиця'], str):
            item['Столиця'] = self.clean_capital(item['Столиця'])
        return item



class SaveToDatabasePipeline:
    def __init__(self):
        self.connection = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=DESKTOP-T94V6UV\\SQLEXPRESS;'
            'DATABASE=CountriesDB;'
            'Trusted_Connection=yes;'
        )
        self.cursor = self.connection.cursor()
    
    def process_item(self, item, spider):
        self.cursor.execute("""
            INSERT INTO Countries (name, url, capital, languages, independence, currency, phone_code, flag_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['Країна'],
            item['URL'],
            item['Столиця'],
            item['Офіційні мови'],
            item['Незалежність'],
            item['Валюта'],
            item['Телефонний код'],
            item.get('flag_url', '') 
        ))
        self.connection.commit()
        return item
    
    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()


class FlagImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'flag_url' in item and item['flag_url']:
            yield Request(url=item['flag_url'], meta={'item': item})
    
    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta['item']
        country_name = item['Країна'].replace(" ", "_")
        image_name = f"{country_name}.jpg"
        return os.path.join('flags_images', image_name)
    
    def item_completed(self, results, item, info):
        if results and results[0][0]:
            image_path = results[0][1]['path']
            item['flag_url'] = image_path  
        return item


