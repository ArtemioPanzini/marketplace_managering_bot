import os
import json
from datetime import datetime, timezone, timedelta, time
from xml.etree import ElementTree as ET
import re


def str_to_time(time_str):
    return datetime.strptime(time_str, "%H:%M").time()


class StoreSettings:
    def __init__(self, settings):
        self.business_id = settings['business_id']
        self.warehouse_id = settings['warehouse_id']
        self.y_sklad_id = settings['y_sklad_id']
        self.stocks = settings['stocks']
        self.minimum_stock = settings['minimum_stock']
        self.prices = settings['prices']
        self.minimum_price = settings['minimum_price']
        self.discount_time = settings['discounts']['discount_time']

        # Распределение скидок для каждого поставщика
        self.artelamp = self.initialize_discount(settings['artelamp'])
        self.favourite = self.initialize_discount(settings['favourite'])
        self.lightstar = self.initialize_discount(settings['lightstar'])
        self.maytoni = self.initialize_discount(settings['maytoni'])
        self.sonex = self.initialize_discount(settings['sonex'])
        self.stilfort = self.initialize_discount(settings['stilfort'])

    def initialize_discount(self, supplier):
        return {
            "work_time": supplier['work_time'],
            "rest_day": supplier['rest_day'],
            "weekends": supplier['weekends'],
            "discount_value": supplier['discount_value']
        }

    def update_discount_multiplier(self, brand):
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%A")

        brand_settings = getattr(self, brand)
        discount_time = self.discount_time


        print(f"1 {current_day} {discount_time['weekends']} {brand_settings['weekends']}")
        print(f"2 {current_time} {str_to_time(discount_time['work_time'][0])} {str_to_time(discount_time['work_time'][1])} {brand_settings['work_time']}")
        print(f"3 {current_time} {str_to_time(discount_time['rest_day'][0])} {str_to_time(discount_time['rest_day'][1])} {brand_settings['rest_day']}")

        if current_day in discount_time['weekends'] and brand_settings['weekends']:
            self.discount_multiplier = brand_settings['discount_value']
            print(f"1 {self.discount_multiplier}")
        elif str_to_time(discount_time['work_time'][0]) <= current_time <= str_to_time(
                discount_time['work_time'][1]) and brand_settings['work_time']:
            self.discount_multiplier = brand_settings['discount_value']
            print(f"2 {self.discount_multiplier}")
        elif (str_to_time(discount_time['rest_day'][0]) <= current_time <= time.max or
              time.min <= current_time <= str_to_time(discount_time['rest_day'][1])) and \
                brand_settings['rest_day']:
            self.discount_multiplier = brand_settings['discount_value']
            print(f"3 {self.discount_multiplier}")
        else:
            self.discount_multiplier = 1
            print("Default condition")


def convert_stock_value(text):
    if text == "более 50":
        return 51
    elif text == "-1":
        return 0
    elif text == "более 10":
        return 11
    else:
        # Используем регулярное выражение для извлечения числа из текста
        match = re.search(r'\d+(\.\d+)?', text)
        if match:
            return float(match.group())
        else:
            return 0  # Если не удается извлечь число, возвращаем 0


def process_offer(offer, article_path, stock_path, price_path, settings):
    article_element = offer.find(article_path)
    if article_element is not None and article_element.text is not None:
        article = article_element.text.replace(' ', '-').replace(',', '-')
    elif offer.get('Имя') is not None:
        article = offer.get('Имя')
    else:
        article = None
    stock_element = offer.find(stock_path)
    if stock_element is not None and isinstance(stock_element, ET.Element) and stock_element.text is not None:
        stock_text = stock_element.text
        stock = convert_stock_value(stock_text) if convert_stock_value(stock_text) > settings.minimum_stock else 0
    else:
        stock = 0

    price_full = int(round(float(offer.find(price_path).text.replace(",", ".")))) * settings.discount_multiplier
    current_time_utc = datetime.now(timezone.utc)
    offset = timedelta(hours=3)  # смещение на 3 часа вперед
    current_time_with_offset = current_time_utc.astimezone(timezone(offset))
    current_time_iso8601 = current_time_with_offset.strftime("%Y-%m-%dT%H:%M:%S%z")

    if price_full > settings.minimum_price:
        stock_entry = {
            "sku": f"{article}",
            "warehouseId": settings.warehouse_id,
            "items": [
                {
                    "count": stock,
                    "type": "FIT",
                    "updatedAt": current_time_iso8601
                }
            ]
        }
        price_entry = {
            "offerId": f"{article}",
            "price": {
                "value": price_full,
                "currencyId": "RUR"
            }
        }
        return stock_entry, price_entry
    else:
        return None, None


def process_xml(file_path, settings):
    root = ET.parse(file_path).getroot()
    stock_data = []
    price_data = []
    if "artelamp.xml" in file_path:
        settings.update_discount_multiplier('artelamp')
        print(settings.discount_multiplier)
        offers = root.findall('.//offer')
        for offer in offers:
            stock_entry, price_entry = process_offer(offer, './vendorCode', './stock',
                                                     './price', settings)
            if stock_entry and price_entry:
                stock_data.append(stock_entry)
                price_data.append(price_entry)
        price_data.append("artelamp.xml")

    elif "favourite.xml" in file_path:
        settings.update_discount_multiplier('favourite')
        print(settings.discount_multiplier)
        items = root.findall(".//Номенклатура")
        for item in items:
            stock_entry, price_entry = process_offer(item, './Имя', './Остаток', './ЦенаРРЦ',
                                                     settings)
            if stock_entry and price_entry:
                stock_data.append(stock_entry)
                price_data.append(price_entry)
        price_data.append("favourite.xml")

    if "lightstar.xml" in file_path:
        settings.update_discount_multiplier('lightstar')
        print(settings.discount_multiplier)
        offers = root.findall('.//offer')
        for offer in offers:
            stock_entry, price_entry = process_offer(offer, './vendorCode', './stock',
                                                     './price', settings)
            if stock_entry and price_entry:
                stock_data.append(stock_entry)
                price_data.append(price_entry)
        price_data.append("lightstar.xml")

    elif "stilfort.xml" in file_path:
        settings.update_discount_multiplier('stilfort')
        print(settings.discount_multiplier)
        offers = root.findall('.//offer')
        for offer in offers:
            stock_entry, price_entry = process_offer(offer, './Артикул', './param[@name="Остатки"]',
                                                     './price',
                                                     settings)
            if stock_entry and price_entry:
                stock_data.append(stock_entry)
                price_data.append(price_entry)
        price_data.append("stilfort.xml")

    elif "sonex.xml" in file_path:
        settings.update_discount_multiplier('sonex')
        print(settings.discount_multiplier)
        items = root.findall(".//item")
        for item in items:
            stock_entry, price_entry = process_offer(item, './article', './stock', './price',
                                                     settings)
            if stock_entry and price_entry:
                stock_data.append(stock_entry)
                price_data.append(price_entry)
        price_data.append("sonex.xml")

    elif "maytoni.xml" in file_path:
        settings.update_discount_multiplier('maytoni')
        print(settings.discount_multiplier)
        offers = root.findall('.//offer')
        for offer in offers:
            stock_entry, price_entry = process_offer(offer, './vendorCode', './outlet/instock', './price',
                                                     settings)
            if stock_entry and price_entry:
                stock_data.append(stock_entry)
                price_data.append(price_entry)
        price_data.append("maytoni.xml")

    return stock_data, price_data


def main():
    # Чтение JSON-файла
    with open('data\\user\\78527993.json', 'r') as file:
        # Загружаем JSON-данные из файла
        data = json.load(file)

        # Создание экземпляра класса
        settings = StoreSettings(data)

        all_stock_entries = []  # Создаем пустой список для всех записей о складах
        all_price_entries = []  # Создаем пустой список для всех записей о ценах

        # Обход папки XML
        for file_name in os.listdir('data/xml'):
            if file_name.endswith('.xml'):
                file_path = os.path.join('data/xml', file_name)
                stock_entries, price_entries = process_xml(file_path, settings)
                all_stock_entries.extend(stock_entries)
                all_price_entries.extend(price_entries)

        # Сохраняем stock_entries и price_entries в файлы
        with open('stock_entries.txt', 'w') as stock_file:
            json.dump(all_stock_entries, stock_file, indent=4)

        with open('price_entries.txt', 'w') as price_file:
            json.dump(all_price_entries, price_file, indent=4)


if __name__ == "__main__":
    main()
