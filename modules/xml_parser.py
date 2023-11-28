import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime

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
