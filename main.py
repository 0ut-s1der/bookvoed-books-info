import json
import os.path
import random
import time

from bs4 import BeautifulSoup
import requests

url = "https://www.bookvoed.ru/"
headers={
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

def main():
    req = requests.get(url)
    src = req.text

    with open("bookvoed.html", "w", encoding="utf-8") as file:
        file.write(src)

    with open("bookvoed.html", encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    bookvoed_genres = soup.find_all("li", class_="UF")
    book_genres_hrefs= {}

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
            if os.path.exists(f'files/{i_url[0]}_{offset//60}.html') == 0:
                try:
                    req = requests.get(f'{i_url[1]}&offset={offset}', headers=headers)
                except Exception as Ex:
                    print(Ex)
                    offset += 60
                    continue

                with open(f'files/{i_url[0]}_{offset//60}.html', "w", encoding="utf-8") as file:
                    file.write(req.text)

            with open(f'files/{i_url[0]}_{offset//60}.html', encoding="utf-8") as file:
                src = file.read()
            soup = BeautifulSoup(src, "lxml")
            if offset == 0:
                i_name = soup.find("div", class_="td lz").find("h1", class_="mz").text
                if os.path.exists(f'books_json/{i_name}.json'):
                    print(f"{i_name} уже существует")
                    already_exists = True
                    break

            books = soup.find_all("div", class_="Qh")
            if len(books) == 0:
                break

            for book in books:
                try:

                    b_href = book.find("a").get("href")
                    b_image = url + book.find("img").get("src")
                    b_name = book.find("a", class_="TUb os").text.replace("\n"," ").strip()
                    b_author = book.find("div", class_="ps").text.replace("\n"," ").strip()
                    b_price = book.find("div", class_="zg")
                    if b_price.find("div", class_="ss"):
                        b_price =b_price.find("div", class_="Ag").text.replace("\n", " ").strip().replace("\u202f₽", " р.")\
                        + " (" + b_price.find("div", class_="ss").text.replace("\n", " ").strip().replace("\u202f₽", " р.")+")"
                    elif b_price.find("div", class_="Ag"):
                        b_price = b_price.find("div", class_="Ag").text.replace("\n", " ").strip().replace("\u202f₽", " р.")
                    elif b_price.find("div", class_="Bg"):
                        b_price = b_price.find("div", class_="Bg").text.replace("\n", " ").strip()

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
            print(f'Категория {i_name}: {offset//60}')
            time.sleep(random.randrange(2,4))
        if already_exists == False:
            with open(f"books_json/{i_name}.json", "a", encoding="utf-8") as file:
                json.dump(one_more_genre, file, indent=4, ensure_ascii=False)
            print(f'Категория {i_name} успешно выгружена')

if __name__ == '__main__':
    main()