import time
import logging
import os
import requests
from concurrent.futures import ThreadPoolExecutor


class XMLDownloader:
    def __init__(self, url, name, directory='.'):
        self.url = url
        self.name = name
        self.directory = directory

    def download_xml(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                filename = os.path.join(self.directory, f"{self.name}.xml")
                print(f"Начинаем качать {filename}.")
                with open(filename, 'wb') as file:
                    file.write(response.content)
                logging.info(f"Файл {filename} успешно скачан.")
                print(f"Файл {filename} успешно скачан.")
            else:
                logging.error(f"Не удалось скачать файл с URL: {self.url}")
        except requests.RequestException as e:
            logging.error(f"Ошибка: {e}")


def main():
    start_time = time.time()

    if not os.path.exists('data/xml'):
        os.makedirs('data/xml')

    tasks = [
        XMLDownloader('https://ftp.favourite-light.com/ForClients/export/offers.xml',
                      'favourite', 'data/xml').download_xml,

        XMLDownloader('https://wbs.e-teleport.ru/Catalog_GetSharedCatalog?contact=lobachev@technolight.ru&catalog_type=yandex',
                      'artelamp', 'data/xml').download_xml,

        XMLDownloader('https://lightstar.ru/image/yml/lightstar_rozn_dolgop_stock.yml',
                      'lightstar', 'data/xml').download_xml,

        XMLDownloader('https://mais-upload.maytoni.de/YML/all.yml',
                      'maytoni', 'data/xml').download_xml,

        XMLDownloader('https://isonex.ru/upload/stocks.xml',
                      'sonex', 'data/xml').download_xml,

        XMLDownloader('https://stilfort.com/admin/exchange/get_export/3965/?as_file=1',
                      'stilfort', 'data/xml').download_xml
    ]

    with ThreadPoolExecutor(max_workers=5) as executor:  # Укажите желаемое количество потоков
        executor.map(lambda task: task(), tasks)

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Программа выполнена за {execution_time} секунд.")


if __name__ == "__main__":
    # Создаем папку 'logs', если она еще не существует
    if not os.path.exists('/logs'):
        os.makedirs('/logs')

    # Настраиваем модуль logging
    logging.basicConfig(filename='/logs/download_xml.log', level=logging.INFO)

    # Добавляем обработчик потока, чтобы логи также выводились в консоль
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

    main()
