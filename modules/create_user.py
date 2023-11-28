import json

class DataHandler:
    def __init__(self):
        self.data = {
            "business_id": None,
            "warehouse_id": None,
            "y_sklad_id": None,
            "stocks": None,
            "minimum_stock": None,
            "prices": None,
            "minimum_price": None,
            "discounts": {
                "discount_time": {
                    "work_time": None,
                    "rest_day": None,
                    "weekends": None,
                }
            },
            "artelamp": {"work_time": None, "rest_day": None, "weekends": None, "discount_value": None},
            "favourite": {"work_time": None, "rest_day": None, "weekends": None, "discount_value": None},
            "lightstar": {"work_time": None, "rest_day": None, "weekends": None, "discount_value": None},
            "maytoni": {"work_time": None, "rest_day": None, "weekends": None, "discount_value": None},
            "sonex": {"work_time": None, "rest_day": None, "weekends": None, "discount_value": None},
            "stilfort": {"work_time": None, "rest_day": None, "weekends": None, "discount_value": None}
        }

    def save_to_json(self, filename):
        with open(f'../data/user/{filename}.json', 'w') as f:
            json.dump(self.data, f)

    def get_yes_or_no_input(self, prompt):
        while True:
            user_input = input(prompt).lower()
            if user_input in ['да', 'нет']:
                return user_input == 'да'
            else:
                print("Пожалуйста, введите 'да' или 'нет'.")

    def get_input(self):
        self.data["business_id"] = int(input("Введите business_id: "))
        self.data["warehouse_id"] = int(input("Введите warehouse_id: "))
        self.data["y_sklad_id"] = int(input("Введите y_sklad_id: "))

        stocks_input = self.get_yes_or_no_input("Введите значение для stocks (да/нет): ")
        self.data["stocks"] = stocks_input

        self.data["minimum_stock"] = int(input("Введите minimum_stock: "))

        prices_input = self.get_yes_or_no_input("Введите значение для prices (да/нет): ")
        self.data["prices"] = prices_input

        self.data["minimum_price"] = int(input("Введите minimum_price: "))

        work_start = input("Введите начало рабочего времени (в формате HH:MM): ")
        work_end = input("Введите конец рабочего времени (в формате HH:MM): ")
        self.data["discounts"]["discount_time"]["work_time"] = [work_start, work_end]

        rest_start = input("Введите начало времени отдыха (в формате HH:MM): ")
        rest_end = input("Введите конец времени отдыха (в формате HH:MM): ")
        self.data["discounts"]["discount_time"]["rest_day"] = [rest_start, rest_end]

        self.data["discounts"]["discount_time"]["weekends"] = [
            input("Введите первый день выходного (например, Saturday): "),
            input("Введите второй день выходного (например, Sunday): ")
        ]

        brands = ["artelamp", "favourite", "lightstar", "maytoni", "sonex", "stilfort"]
        for brand in brands:
            work_time_input = self.get_yes_or_no_input(f"Введите значение для {brand}.work_time (да/нет): ")
            rest_day_input = self.get_yes_or_no_input(f"Введите значение для {brand}.rest_day (да/нет): ")
            weekends_input = self.get_yes_or_no_input(f"Введите значение для {brand}.weekends (да/нет): ")

            self.data[brand]["work_time"] = work_time_input
            self.data[brand]["rest_day"] = rest_day_input
            self.data[brand]["weekends"] = weekends_input

            self.data[brand]["discount_value"] = float(input(f"Введите {brand}.discount_value: "))

        self.save_to_json(self.data["warehouse_id"])


# Использование класса
handler = DataHandler()
handler.get_input()
