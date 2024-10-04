import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Настройки для подключения к удаленной отладке Edge
edge_options = Options()
edge_options.add_experimental_option("debuggerAddress", "localhost:9222")

# Подключение к уже запущенному браузеру Edge
driver = webdriver.Edge(options=edge_options)

# Список URL уже скачанных изображений, чтобы избегать дублирования
downloaded_images_urls = set()


# Функция для скачивания изображений
def download_images():
    global downloaded_images_urls

    # Папка для сохранения изображений (предполагаем, что папка уже создана)
    save_folder = 'D:\Mir\Project\Photo'

    # Подсчитываем количество уже существующих изображений в папке
    existing_images = len([f for f in os.listdir(save_folder) if f.endswith('.jpg')])

    # Ищем все изображения с нужным классом
    images = driver.find_elements(By.CSS_SELECTOR, "img.multimedia-image__image.multimedia-image--fit-cover")

    # Начинаем нумерацию новых изображений
    new_image_index = existing_images + 1

    # Скачиваем все изображения
    for img in images:
        # Получаем URL изображения
        img_url = img.get_attribute('src')
        if img_url.startswith("//"):
            img_url = 'https:' + img_url

        # Пропускаем уже скачанные изображения
        if img_url in downloaded_images_urls:
            continue

        # Имя файла для сохранения
        img_name = f'image_{new_image_index}.jpg'
        img_path = os.path.join(save_folder, img_name)

        # Скачиваем изображение
        response = requests.get(img_url)
        if response.status_code == 200:
            with open(img_path, 'wb') as img_file:
                img_file.write(response.content)
            print(f'Изображение {img_name} сохранено.')
            downloaded_images_urls.add(img_url)  # Добавляем URL в список скачанных
            new_image_index += 1
        else:
            print(f'Ошибка загрузки изображения {img_name}.')


# Функция для программного клика по кнопке с использованием Selenium
# Функция для программного клика по кнопке с использованием Selenium
def go_to_next():
    try:
        # Явное ожидание для кнопки "next"
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="page-container"]/div/div/div[2]/div[2]/div/div/div[3]/div/div/div[2]/div/button'))
        )
        next_button.click()  # Программный клик по кнопке

        print("Переход на следующую страницу с помощью Selenium.")

        # Ожидание до тех пор, пока старая картинка исчезнет
        WebDriverWait(driver, 10).until(
            EC.staleness_of(driver.find_element(By.CSS_SELECTOR, "img.multimedia-image__image.multimedia-image--fit-cover"))
        )
        time.sleep(1)  # Небольшая пауза для загрузки новой страницы

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Ошибка: {str(e)}")
        return False
    return True


# Переход на сайт
driver.get('https://badoo.com/uk/encounters')

# Подождите, пока страница полностью загрузится
time.sleep(10)

# Основной цикл: скачивание изображений и переход на следующую страницу
while True:
    download_images()  # Скачиваем изображения
    if not go_to_next():  # Переходим на следующую страницу с помощью Selenium
        break  # Если что-то пошло не так, выходим из цикла

print('Загрузка завершена.')

# Закрываем браузер
driver.quit()