import time
from selenium.webdriver.common.by import By

def func2(driver):
    usuario = input("Digite o nome do usuário: ").strip()
    driver.get(f"https://www.instagram.com/{usuario}/")
    time.sleep(3)
    follow_button = driver.find_element(By.XPATH, "//button[text()='Seguir']")
    follow_button.click()
