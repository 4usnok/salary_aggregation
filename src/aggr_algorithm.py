import json
from collections import defaultdict
from datetime import datetime
import bson


def read_file_bson(file_path):
    """Чтение файла .bson"""
    with open(file_path, "rb") as f:
        data = bson.decode_all(f.read())
        return data


def save_in_json(dt_from, dt_upto, group_type):
    """Алгоритм для агрегации сумм выплат по периодам"""
    try:
        # Преобразуем входные строки в datetime
        dt_from_obj = datetime.fromisoformat(dt_from)
        dt_upto_obj = datetime.fromisoformat(dt_upto)

        # Читаем файл
        data = read_file_bson("./data/sample_collection.bson")

        # Словарь для суммирования выплат по периодам
        grouped_sums = defaultdict(int)

        for dictionary in data:
            dt_value = dictionary.get("dt")  # вычленяем 'dt'
            value = dictionary.get("value")  # вычленяем 'value'

            if dt_from_obj <= dt_value <= dt_upto_obj:
                # Определяем ключ группировки
                if group_type == "hour":
                    # Группировка по часам
                    key = dt_value.replace(minute=0, second=0, microsecond=0)
                elif group_type == "day":
                    # Группировка по дням
                    key = dt_value.replace(hour=0, minute=0, second=0, microsecond=0)
                elif group_type == "month":
                    # Группировка по месяцам (первое число месяца)
                    key = dt_value.replace(
                        day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                elif group_type == "year":
                    # Группировка по годам (первое число года)
                    key = dt_value.replace(
                        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
                    )
                else:
                    key = dt_value  # Без группировки

                # Суммируем выплаты для этого периода
                grouped_sums[key] += value

        # Сортируем периоды по дате
        sorted_periods = sorted(grouped_sums.keys())

        # Формируем итоговые списки
        labels = []
        dataset = []

        for period in sorted_periods:
            # Форматируем label как в примере (первое число месяца)
            if group_type == "month":
                label = period.isoformat()  # Уже первое число месяца
            elif group_type == "day":
                label = period.isoformat()  # Уже начало дня
            elif group_type == "hour":
                label = period.isoformat()  # Уже начало часа
            elif group_type == "year":
                label = period.isoformat()  # Уже начало года
            else:
                label = period.isoformat()

            labels.append(label)
            dataset.append(grouped_sums[period])  # Сумма выплат за период

        result = {"dataset": dataset, "labels": labels}

        with open("./data/pars_file.json", "w", encoding="utf-8") as new_file:
            json.dump(result, new_file, ensure_ascii=False, indent=2, default=str)
            print("✅ JSON-файл с агрегациями создан")
            return result

    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return None
