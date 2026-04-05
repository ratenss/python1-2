# Версия с автоматическим открытием браузера
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager  # Автоматически установит драйвер
from openpyxl import Workbook

# --- НАСТРОЙКИ ---
BASE_URL = 'https://www.onlinetrade.ru/catalogue/operativnaya_pamyat-c341/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Классы, которые ты нашел в инспекторе
CLASS_PRODUCT_BLOCK = 'k_centered'           # div с товаром
CLASS_TITLE = 'indexGoods__item__name'       # а с названием
CLASS_PRICE = 'price js__actualPrice'        # span с ценой


def setup_driver():
    """Настраивает и возвращает WebDriver для Chrome с автоматической установкой драйвера."""
    print("🔄 Настройка браузера...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--headless=new')  # Фоновый режим
    options.add_argument(f'user-agent={HEADERS["User-Agent"]}')

    # Автоматическая установка и настройка драйвера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Браузер готов.")
    return driver


def parse_page(driver, url):
    print(f"🌐 Загружаю: {url}")
    driver.get(url)
    time.sleep(3)  # даём странице первоначально загрузиться

    # Прокручиваем вниз, чтобы активировать ленивую загрузку
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    try:
        # Ждём появления хотя бы одного элемента с классом, содержащим 'k_centered' (или любым другим)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*=k_centered]"))
        )
    except TimeoutException:
        print("❌ Таймаут: карточки товаров не загрузились.")
        # Дополнительно: выводим кусок исходного кода страницы для отладки
        print("HTML страницы (первые 500 символов):", driver.page_source[:500])
        return []

    # Находим блоки. Используем CSS-селектор на всякий случай
    product_blocks = driver.find_elements(By.CSS_SELECTOR, "[class*=k_centered]")
    print(f"Найдено блоков: {len(product_blocks)}")
    if not product_blocks:
        return []

    products_on_page = []
    for block in product_blocks:
        # Название (ищем любой элемент с классом, содержащим 'indexGoods__item__name')
        title_elem = block.find_element(By.CSS_SELECTOR, "[class*=indexGoods__item__name]")
        title = title_elem.text.strip() if title_elem else "Нет названия"

        # Цена (ищем элемент с классом, содержащим 'price')
        price_elem = block.find_element(By.CSS_SELECTOR, "[class*=price]")
        price = price_elem.text.strip() if price_elem else "Нет цены"

        # Ссылка
        link = title_elem.get_attribute('href') if title_elem else ""

        products_on_page.append({'title': title, 'price': price, 'link': link})
    return products_on_page


def save_to_excel(data, filename='operativnaya_pamyat.xlsx'):
    """Сохраняет список товаров в Excel-файл."""
    if not data:
        print("Нет данных для сохранения.")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Оперативная память"
    ws.append(['Название', 'Цена', 'Ссылка'])

    for row in data:
        ws.append([row['title'], row['price'], row['link']])

    wb.save(filename)
    print(f"💾 Сохранено {len(data)} товаров в файл '{filename}'.")


def main():
    driver = setup_driver()
    all_products = []

    # --- ПАГИНАЦИЯ ---
    page_num = 1               # Начинаем с 1
    max_pages = 20             # Подстраховка, чтобы не уйти в бесконечность

    while page_num <= max_pages:
        # Формируем URL: для первой страницы параметр не нужен
        if page_num == 1:
            url = BASE_URL
        else:
            # Для второй и следующих добавляем параметр ?page=N-1
            url = f"{BASE_URL}?page={page_num - 1}"

        products = parse_page(driver, url)
        if not products:
            print("🏁 Товары на странице не найдены. Завершаем.")
            break

        all_products.extend(products)
        page_num += 1
        time.sleep(2)  # Пауза между запросами, чтобы не нагружать сервер

    driver.quit()
    save_to_excel(all_products)
    print(f"🎉 Готово! Всего собрано товаров: {len(all_products)}")


if __name__ == '__main__':
    main()