import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import Workbook

# --- НАСТРОЙКИ ---
BASE_URL = 'https://www.onlinetrade.ru/catalogue/operativnaya_pamyat-c341/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Классы (ты нашёл их в инспекторе)
CLASS_PRODUCT_BLOCK = 'k_centered'           # блок товара
CLASS_TITLE = 'indexGoods__item__name'       # название
CLASS_PRICE = 'price js__actualPrice'        # цена


def setup_driver():
    """Настраивает браузер (без headless, чтобы видеть капчу)."""
    print("🔄 Настройка браузера...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # Не используем headless — иначе капчу не ввести
    options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Браузер готов. Если появится капча — введи её вручную в открывшемся окне.")
    return driver


def parse_page(driver, url, page_num):
    """Загружает страницу, ждёт появления товаров (до 60 сек), возвращает список."""
    print(f"🌐 Загружаю страницу {page_num}: {url}")
    driver.get(url)

    # Даём время на ручное решение капчи (30 сек). Можно увеличить до 60.
    print("⏳ Ожидание 30 секунд на случай капчи. Если капча есть — введи и жди.")
    time.sleep(30)

    # Прокрутка вниз для активации lazy loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    # Ждём появления хотя бы одного блока товара (увеличенный тайм-аут)
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*=k_centered]"))
        )
    except TimeoutException:
        print("❌ Таймаут 60 сек: карточки товаров не загрузились.")
        print("HTML страницы (первые 800 символов):", driver.page_source[:800])
        return []

    # Находим все блоки товаров
    product_blocks = driver.find_elements(By.CSS_SELECTOR, "[class*=k_centered]")
    print(f"✅ Найдено блоков товаров: {len(product_blocks)}")
    if not product_blocks:
        return []

    products = []
    for block in product_blocks:
        # Название
        try:
            title_elem = block.find_element(By.CSS_SELECTOR, "[class*=indexGoods__item__name]")
            title = title_elem.text.strip()
        except NoSuchElementException:
            title = "Нет названия"
            title_elem = None

        # Цена
        try:
            price_elem = block.find_element(By.CSS_SELECTOR, "[class*=price]")
            price = price_elem.text.strip()
        except NoSuchElementException:
            price = "Нет цены"

        # Ссылка
        link = title_elem.get_attribute('href') if title_elem else ""

        products.append({
            'title': title,
            'price': price,
            'link': link
        })
    return products


def save_to_excel(data, filename='operativnaya_pamyat.xlsx'):
    """Сохраняет список товаров в Excel."""
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
    print(f"💾 Сохранено {len(data)} товаров в '{filename}'.")


def main():
    driver = setup_driver()
    all_products = []
    MAX_PAGES = 3  # только 3 страницы для теста

    for page_num in range(1, MAX_PAGES + 1):
        if page_num == 1:
            url = BASE_URL
        else:
            # Вторая страница = ?page=1, третья = ?page=2 и т.д.
            url = f"{BASE_URL}?page={page_num - 1}"

        products = parse_page(driver, url, page_num)
        if not products:
            print(f"🏁 На странице {page_num} товары не найдены. Останавливаемся.")
            break

        all_products.extend(products)
        time.sleep(3)  # пауза между страницами

    driver.quit()
    save_to_excel(all_products)
    print(f"🎉 Готово! Всего собрано товаров: {len(all_products)}")


if __name__ == '__main__':
    main()