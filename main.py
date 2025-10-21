from src.aggr_alg import read_file_bson, save_in_json

# Читаем файл
data = read_file_bson("./data/sample_collection.bson")
# Параметры для настройки сохранения зарплат
save_in_json("2022-01-01 00:00:00", "2022-12-31T00:00:00", "day")
