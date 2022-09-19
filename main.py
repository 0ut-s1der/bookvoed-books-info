import json
import os.path
import random
import time
import re

from bs4 import BeautifulSoup
import requests

url = "https://www.bookvoed.ru/"
url_help = "https://www.bookvoed.ru/books?genre=2710"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

class_name = "FVb os"
class_author = "ps"
class_price = "zg ts"
class_price_1 = "ss"
class_price_2 = "Ag"
class_price_3 = "Bg"
class_names = []


def get_class_names():
    r = requests.get("")


def main():
    req = requests.get(url)
    src = req.text

    with open("bookvoed.html", "w", encoding="utf-8") as file:
        file.write(src)

    with open("bookvoed.html", encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")

    class_title_1 = soup.find('h2')['class']
    class_genres = soup.find('li')['class']
    bookvoed_genres = soup.find_all("li", class_=class_genres)
    book_genres_hrefs = {}

    if os.path.exists("books_json/") == 0:
        os.mkdir("books_json/")
    if os.path.exists("files/") == 0:
        os.mkdir("files/")

    for i in bookvoed_genres:
        x = i.find("a")
        if int(i["data-genre"]) > 100:
            book_genres_hrefs[f'{x.text}_{i["data-genre"]}'] = x.get("href")

    ex = False

    for i_url in book_genres_hrefs.items():
        if ex:
            contin = input("Выгрузить следующую категорию? [да]")
            if contin != "" and contin != "да":
                print("Выход...")
                break
        else:
            ex = True

        offset = 0
        one_more_genre = []
        already_exists = False

        while True:
            if os.path.exists(f'files/{i_url[0]}_{offset // 60}.html') == 0:
                try:
                    req = requests.get(f'{i_url[1]}&offset={offset}', headers=headers)
                except Exception as Ex:
                    print(Ex)
                    offset += 60
                    continue

                with open(f'files/{i_url[0]}_{offset // 60}.html', "w", encoding="utf-8") as file:
                    file.write(req.text)

            with open(f'files/{i_url[0]}_{offset // 60}.html', encoding="utf-8") as file:
                src = file.read()
            soup = BeautifulSoup(src, "lxml")
            if offset == 0:
                i_name = soup.find("h1", class_=class_title_1).text
                if os.path.exists(f'books_json/{i_name}.json'):
                    print(f"{i_name} уже существует")
                    already_exists = True
                    break

            if not class_names:
                req = requests.get(url_help)
                soup_help = BeautifulSoup(req.text, 'lxml')
                class_names.append(soup_help.find('a', string=re.compile("Портрет")).parent.parent.parent['class'][0])
                class_names.append(soup_help.find('a', string=re.compile("Портрет"))['class'][0])
                class_names.append(
                    soup_help.find('div', class_="Qh").find(string=re.compile("Уайльд")).parent['class'][0])
                class_names.append(soup_help.find('div', string=re.compile("₽")).parent.parent['class'][0])

            books = soup.find_all("div", class_=class_names[0])
            if len(books) == 0:
                break

            for book in books:
                try:
                    b_href = book.find("a").get("href")
                    b_image = url + book.find("img").get("src")
                    b_name = book.find("a", class_=class_names[1]).text.replace("\n", " ").strip()
                    b_author = book.find("div", class_=class_names[2]).text.replace("\n", " ").strip()
                    b_price = book.find("div", class_=class_names[3])
                    if b_price.find("div", class_=class_price_1):
                        b_price = b_price.find("div", class_=class_price_2).text.replace("\n", " ").strip().replace(
                            "\u202f₽",
                            " р.") \
                                  + " (" + b_price.find("div", class_=class_price_1).text.replace("\n",
                                                                                                  " ").strip().replace(
                            "\u202f₽", " р.") + ")"
                    elif b_price.find("div", class_=class_price_2):
                        b_price = b_price.find("div", class_=class_price_2).text.replace("\n", " ").strip().replace(
                            "\u202f₽",
                            " р.")
                    elif b_price.find("div", class_=class_price_3):
                        b_price = b_price.find("div", class_=class_price_3).text.replace("\n", " ").strip()

                except Exception as Ex:
                    print(Ex)
                    offset += 60
                    continue
                one_more_genre.append(
                    {
                        "Автор": b_author,
                        "Название": b_name,
                        "Цена": b_price,
                        "Обложка": b_image,
                        "Ссылка": b_href
                    }
                )
            offset += 60
            print(f'Категория {i_name}: {offset // 60}')
            time.sleep(random.randrange(2, 4))
        if already_exists == False:
            with open(f"books_json/{i_name}.json", "a", encoding="utf-8") as file:
                json.dump(one_more_genre, file, indent=4, ensure_ascii=False)
            print(f'Категория {i_name} успешно выгружена')


if __name__ == '__main__':
    main()
