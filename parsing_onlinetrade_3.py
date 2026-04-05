# Версия для 1 предмета
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = 'https://www.onlinetrade.ru/catalogue/operativnaya_pamyat-c341/'

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_first_product():
    driver = setup_driver()
    driver.get(BASE_URL)
    print("⏳ 30 секунд на ручное решение капчи (если появится)...")
    time.sleep(30)

    try:
        # Ждём первый блок товара
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*=k_centered]"))
        )
    except:
        print("❌ Товары не загрузились.")
        driver.quit()
        return None

    # Берём первый блок
    first_block = driver.find_element(By.CSS_SELECTOR, "[class*=k_centered]")
    try:
        title = first_block.find_element(By.CSS_SELECTOR, "[class*=indexGoods__item__name]").text
    except:
        title = "Нет названия"
    try:
        price = first_block.find_element(By.CSS_SELECTOR, "[class*=price]").text
    except:
        price = "Нет цены"

    driver.quit()
    return {"title": title, "price": price}

if __name__ == '__main__':
    product = get_first_product()
    if product:
        print(f"✅ Название: {product['title']}\n💰 Цена: {product['price']}")
    else:
        print("Не удалось.")