import os
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
import warnings
from openpyxl import Workbook

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

FOLDER = '.'


def detect_encoding(filepath):
    """Пробует разные кодировки и возвращает рабочую"""
    encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                f.read()
            return enc
        except UnicodeDecodeError:
            continue
    return 'utf-8'  # fallback


def parse_html_file(filepath):
    encoding = detect_encoding(filepath)
    print(f"  Кодировка файла: {encoding}")
    with open(filepath, 'r', encoding=encoding) as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    products = []
    items = soup.find_all('div', class_='indexGoods__item')
    print(f"  Найдено блоков: {len(items)}")

    for item in items:
        title_tag = item.find('a', class_='indexGoods__item__name')
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.get('href', '')
        if link and not link.startswith('http'):
            link = 'https://www.onlinetrade.ru' + link

        price_tag = item.find('span', class_='price js__actualPrice')
        if not price_tag:
            price_tag = item.find('div', class_='price js__actualPrice')
        price = price_tag.get_text(strip=True) if price_tag else 'Нет цены'

        products.append([title, price, link])
    return products


def main():
    all_products = []
    page_num = 1
    while True:
        filename = os.path.join(FOLDER, f'page{page_num}.html')
        if not os.path.exists(filename):
            print(f"Файл {filename} не найден, останавливаемся.")
            break
        print(f"Обрабатываю {filename}...")
        products = parse_html_file(filename)
        print(f"  Извлечено товаров: {len(products)}")
        all_products.extend(products)
        page_num += 1

    if not all_products:
        print("Ни одного товара не найдено. Проверь, что файлы содержат HTML-код (открой их в браузере).")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Оперативная память"
    ws.append(['Название', 'Цена', 'Ссылка'])
    for row in all_products:
        ws.append(row)
    output_file = 'operativnaya_pamyat_manual.xlsx'
    wb.save(output_file)
    print(f"\n✅ Готово! Собрано {len(all_products)} товаров. Результат в '{output_file}'.")


if __name__ == '__main__':
    main()