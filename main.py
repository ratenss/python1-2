import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from openpyxl import Workbook  # библиотека для работы с Excel

base_url = 'https://www.onlinetrade.ru/catalogue/operativnaya_pamyat-c341/'

# обход блокировки (ошибка 403)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# функция для парсинга одной страницы (загружает страницу и извлекает список товаров)
def parse_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return []

    products_on_page = []
    # поиск всех блоков с товарами
    product_blocks = soup.find_all('div', class_='k_centered')

    for block in product_blocks:
        # извлечение название оперативной памяти
        title_tag = block.find('a', class_='indexGoods__item__name')
        title = title_tag.text.strip() if title_tag else 'Нет названия'

        # извлечение цены
        price_tag = block.find('span', class_='price js__actualPrice')
        if not price_tag:
            price_tag = block.find('div', class_='price js__actualPrice')
        price = price_tag.text.strip() if price_tag else 'Нет цены'

        # извлечение ссылки на товар
        link = title_tag['href'] if title_tag and title_tag.has_attr('href') else ''
        if link and not link.startswith('http'):
            # дополнение ссылки до полного URL, если она относительная
            link = 'https://www.onlinetrade.ru' + link

        products_on_page.append({
            'title': title,
            'price': price,
            'link': link
        })
    return products_on_page

# основной цикл для прохода по всем страницам
def main():
        all_products = []
        page_num = 0  # начинаем с 0
        max_pages = 20

        while page_num < max_pages:
            if page_num == 0:
                page_url = base_url  # первая страница без параметров
            else:
                page_url = f"{base_url}?page={page_num}"  # вторая и так далее

            print(f"Парсим страницу {page_num + 1}: {page_url}")
            products = parse_page(page_url)
            if not products:
                print(f"На странице {page_num + 1} товаров не найдено. Завершаем.")
                break

            all_products.extend(products)
            page_num += 1
            time.sleep(1)

    # сохранение результатов в .xlsx
        if all_products:
        # создание новой Excel-книги
            wb = Workbook()
            ws = wb.active
            ws.title = "Оперативная память"

        # добавление заголовки столбцов
            ws.append(['Название', 'Цена', 'Ссылка'])

        # добавление данных о каждом товаре
            for product in all_products:
                ws.append([product['title'], product['price'], product['link']])

        # сохранение файла
            filename = 'operativnaya_pamyat.xlsx'
            wb.save(filename)
            print(f"\nГотово! Собрано {len(all_products)} товаров. Результат сохранен в файл '{filename}'.")
        else:
            print("Не удалось найти ни одного товара. Проверьте селекторы.")

if __name__ == '__main__':
    main()