import json
import os.path
import pandas as pd

if os.path.exists("books_exel/") == 0:
    os.mkdir("books_exel/")
list_json = os.listdir("books_json")
try:
    for i in list_json:
        if os.path.exists(f'./books_exel/{i.split(".j")[0]}.xlsx'):
            continue
        with open(f"books_json/{i}", encoding="utf-8") as file:
            df = pd.DataFrame(json.load(file))
        df.to_excel(f'./books_exel/{i.split(".j")[0]}.xlsx')
    print("Работа успешно завершена")
except Exception as e:
    print(f'Произошла ошибка. {e}')
