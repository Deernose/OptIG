import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def func3(driver):
    termo = input("Digite o termo: ").strip()
    search_box = driver.find_element(By.XPATH, "//input[@placeholder='Pesquisar']")
    search_box.clear()
    search_box.send_keys(termo)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
