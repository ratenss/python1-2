# Подключение инструментов (импорты)
import requests
import bs4
from bs4 import BeautifulSoup
import csv
import time

# Обход блокировки (ошибка 403)
HEADERS={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Функция загрузки и парсинга сайта
def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе {url}: {e}")
        return None

# Функция взятия цитат из супа
def parse_quotes(soup):
    quotes_data = []
    quote_divs = soup.find_all('div', class_='quote')

    for quote in quote_divs:
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        tags = [tag.text for tag in quote.find_all('a', class_='tag')]
        quotes_data.append({
            'text': text,
            'author': author,
            'tags': ', '.join(tags)
        })
    return quotes_data

# Функция сохранения в файл
def save_to_csv(data, filename='quotes.csv'):
    if not data:
        print("Нет данных для сохранения")
        return
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'author', 'tags'])
        writer.writeheader()
        writer.writerows(data)
    print(f"Сохранено {len(data)} записей в {filename}")

def main():
        base_url = 'https://quotes.toscrape.com/'
        all_quotes = []
        page = 1

# Цикл обхода всевозможных страниц
        while True:
            url = f'{base_url}page/{page}/'
            print(f'Парсим страницу {page}...')
            soup = get_soup(url)
            if not soup:
                break

# Парсинг страницы
            quotes_on_page = parse_quotes(soup)
            if not quotes_on_page:
                break
            all_quotes.extend(quotes_on_page)
            page += 1
            time.sleep(1)

# Вывод
        print(f'Всего собрано цитат: {len(all_quotes)}')
        save_to_csv(all_quotes)

        for i, q in enumerate(all_quotes[:3], 1):
            print(f"{i}. {q['text'][:50]}... — {q['author']}")

if __name__ == '__main__': main()