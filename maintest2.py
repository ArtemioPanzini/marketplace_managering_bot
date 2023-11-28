import os
import json
from datetime import datetime
from xml.etree import ElementTree as ET
import re


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

        self.discount_settings = {
            "artelamp": settings['artelamp'],
            "favourite": settings['favourite'],
            "lightstar": settings['lightstar'],
            "maytoni": settings['maytoni'],
            "sonex": settings['sonex'],
            "stilfort": settings['stilfort']
        }

        self.discount_multiplier = 1  # Инициализация значения скидки по умолчанию
        current_time = datetime.now().strftime("%H:%M")
        current_day = datetime.now().strftime("%A")

        for supplier, discount_info in self.discount_settings.items():
            work_time = discount_info['work_time']
            rest_day = discount_info['rest_day']
            weekends = discount_info['weekends']

            if work_time and rest_day and weekends:
                # Если скидка доступна в любое время, включая выходные и дни отдыха
                self.discount_settings[supplier]['discount_value'] = self.discount_multiplier
            elif current_time in work_time.split('-') or (
                    work_time.split('-')[0] < current_time < work_time.split('-')[1]):

                # Если текущее время находится в рабочее время
                self.discount_settings[supplier]['discount_value'] = self.discount_multiplier
            elif current_day == rest_day or current_day in weekends.split(','):
                # Если сегодня выходной или день отдыха
                self.discount_settings[supplier]['discount_value'] = discount_info['discount_value']
            else:
                self.discount_settings[supplier]['discount_value'] = self.discount_multiplier


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

    if price_full > settings.minimum_price:
        stock_entry = {
            "sku": f"{article}",
            "warehouseId": settings.warehouse_id,
            "items": [
                {
                    "count": stock,
                    "type": "FIT",
                    "updatedAt": datetime.now().isoformat()
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

    # Извлечение имени производителя из имени файла
    manufacturer = None
    if "artelamp.xml" in file_path:
        manufacturer = 'artelamp'
    elif "favourite.xml" in file_path:
        manufacturer = 'favourite'
    elif "lightstar.xml" in file_path:
        manufacturer = 'lightstar'
    elif "stilfort.xml" in file_path:
        manufacturer = 'stilfort'
    elif "sonex.xml" in file_path:
        manufacturer = 'sonex'
    elif "maytoni.xml" in file_path:
        manufacturer = 'maytoni'
    if manufacturer:
        # Получение параметров скидки для производителя из настроек
        discount_info = settings.__dict__.get(manufacturer)

        if manufacturer in ["artelamp", "lightstar"]:
            offers = root.findall('.//offer')
            for offer in offers:
                stock_entry, price_entry = process_offer(offer, './vendorCode', './stock',
                                                         './price', settings)
                if stock_entry and price_entry:
                    stock_data.append(stock_entry)
                    price_data.append(price_entry)
            price_data.append("artelamp.xml")

        elif manufacturer == "favourite":

            items = root.findall(".//Номенклатура")

            for item in items:

                stock_entry, price_entry = process_offer(item, './Имя', './Остаток', './ЦенаРРЦ',

                                                         settings)

                if stock_entry and price_entry:
                    stock_data.append(stock_entry)

                    price_data.append(price_entry)

        elif manufacturer == "stilfort":

            offers = root.findall('.//offer')

            for offer in offers:

                stock_entry, price_entry = process_offer(offer, './Артикул', './param[@name="Остатки"]',

                                                         './price', settings)

                if stock_entry and price_entry:
                    stock_data.append(stock_entry)

                    price_data.append(price_entry)

                    # Установка discount_multiplier на основе данных из настроек

                    settings.discount_multiplier = discount_info['discount_value']

        elif manufacturer == "sonex":
            items = root.findall(".//item")
            for item in items:
                stock_entry, price_entry = process_offer(item, './article', './stock', './price',

                                                         settings)
                if stock_entry and price_entry:
                    stock_data.append(stock_entry)
                    price_data.append(price_entry)
        elif manufacturer == "maytoni.xml":
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
