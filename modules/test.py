from datetime import datetime, time


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

# Пример использования
discount_params = {
    'discount_time': {
        'work_time': (time(9, 30), time(19, 30)),
        'rest_day': (time(19, 31), time(8, 29)),
        'weekends': ['Saturday', 'Sunday'],  # Указание выходных дней
    },
    'discount_bool': {
        'work_time': True,
        'rest_day': False,
        'weekends': True,  # Установите значение в True для обработки выходных
    },
    'discount_value': 0.9
}
specific_date = datetime(2023, 11, 28, 10, 30, 0)
store_settings = StoreSettings(
    business_id=73939133,
    warehouse_id=68406114,
    y_sklad_id=763847,
    stocks=True,
    minimum_stock=3,
    prices=True,
    minimum_price=4000,
    discount=discount_params
)
store_settings.calculate_discount_values()

# Получение значений настроек
print(f"Discount Value in Code: {store_settings.discount_value_in_code}")

