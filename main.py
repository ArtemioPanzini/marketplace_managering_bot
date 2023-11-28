import os
import json
from datetime import datetime
from xml.etree import ElementTree as ET

class StoreSettings:
    def __init__(self, business_id, warehouse_id, y_sklad_id, stocks, minimum_stock, prices, minimum_price, discount):
        self.business_id = business_id
        self.warehouse_id = warehouse_id
        self.y_sklad_id = y_sklad_id
        self.stocks = stocks
        self.minimum_stock = minimum_stock
        self.prices = prices
        self.minimum_price = minimum_price
        self.discount_time = discount['discount_time']
        self.discount_bool = discount['discount_bool']
        self.discount_value = discount['discount_value']
        self.discount_value_in_code = 1  # Добавлено новое свойство

    def calculate_discount_values(self, current_date=datetime.now()):
        for discount_type, time_range in self.discount_time.items():
            if discount_type == 'weekends':
                if self.check_weekend(current_date) and self.discount_bool[discount_type]:
                    self.discount_value_in_code = self.discount_value
            else:
                start_time, end_time = time_range
                if self.check_time(current_date, start_time, end_time) and self.discount_bool[discount_type]:
                    self.discount_value_in_code = self.discount_value

    def check_time(self, current_date, start_time, end_time):
        current_time = current_date.time()
        return start_time <= current_time <= end_time

    def check_weekend(self, current_date):
        today = current_date.strftime('%A')
        return today in ['Saturday', 'Sunday']


def process_offer(offer, article_path, stock_path, price_path, discount_multiplier, minimum_price, minimum_stock):
    article = offer.find(article_path).text
    article = f"{article.replace(' ', '-').replace(',', '-')}"
    stock = offer.find(stock_path).text
    if stock == "-1" or int(stock) <= minimum_stock:
        stock = 0
    price_full_str = offer.find(price_path).text
    price_full = int(round(float(price_full_str.replace(",", "."))))
    if price_full <= minimum_price:
        return None, None, None
    price_full *= discount_multiplier
    return article, stock, price_full

if "artelamp.xml" in file_path:
    offers = root.findall('.//offer')
    for offer in offers:
        article, stock, price_full = process_offer(offer, './/vendorCode', './/stock',
                                                   './/price', settings.discount_multiplier,
                                                   settings.minimum_price,
                                                   settings.minimum_stock)

elif "favourite.xml" in file_path:
    items = root.findall(".//Номенклатура")
    for item in items:
        article, stock, price_rrc = process_offer(item, './Имя', './Остаток', './ЦенаРРЦ',
                                                  settings.discount_multiplier,
                                                  settings.minimum_price,
                                                  settings.minimum_stock)

elif "stilfort.xml" in file_path:
    offers = root.findall('.//offer')
    for offer in offers:
        article, stock, price_full = process_offer(offer, './/Артикул', './/param[@name="Остатки"]',
                                                   './/price',
                                                   settings.discount_multiplier,
                                                   settings.minimum_price, settings.minimum_stock)

elif "sonex.xml" in file_path:
    items = root.findall(".//item")
    for item in items:
        article, stock, price = process_offer(item, './article', './stock', './price',
                                              settings.discount_multiplier,
                                              settings.minimum_price, settings.minimum_stock)

elif "maytoni.xml" in file_path:
    offers = root.findall('.//offer')
    for offer in offers:
        article, stock, price_full = process_offer(offer, './@id', './outlet/@instock', './price',
                                                   settings.discount_multiplier,
                                                   settings.minimum_price, settings.minimum_stock)


def main():
    # Чтение JSON-файла
    with open('..\\data\\user\\78527993.json', 'r') as file:
        # Загружаем JSON-данные из файла
        data = json.load(file)

    # Создание экземпляра класса
    settings = StoreSettings(
        business_id=data['business_id'],
        warehouse_id=data['warehouse_id'],
        y_sklad_id=data['y_sklad_id'],
        stocks=data['stocks'],
        minimum_stock=data['minimum_stock'],
        prices=data['prices'],
        minimum_price=data['minimum_price'],
        discount=data['discounts']
    )

    # Обход папки XML
    for file_name in os.listdir('path_to_your_xml_folder'):
        if file_name.endswith('.xml'):
            file_path = os.path.join('path_to_your_xml_folder', file_name)
            process_xml(file_path, settings)

if __name__ == "__main__":
    main()
