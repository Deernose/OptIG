import time
import random
import logging
from selenium.webdriver.remote.webdriver import WebDriver

# Configuração de Log
logging.basicConfig(filename='logs/bot_activity.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_message(level, message):
    """Registra uma mensagem no log."""
    if level == 'info':
        logging.info(message)
    elif level == 'warning':
        logging.warning(message)
    elif level == 'error':
        logging.error(message)
    else:
        logging.debug(message) # Para outros níveis não especificados

def random_sleep(min_sec, max_sec):
    """
    Pausa a execução por um tempo aleatório entre min_sec e max_sec.
    Isso ajuda a simular comportamento humano.
    """
    sleep_time = random.uniform(min_sec, max_sec)
    log_message('info', f"Pausando por {sleep_time:.2f} segundos...")
    time.sleep(sleep_time)

def scroll_down(driver: WebDriver, num_scrolls: int = 1, scroll_delay: float = 0.5):
    """
    Rola a página para baixo um número de vezes.
    :param driver: Instância do WebDriver.
    :param num_scrolls: Número de vezes para rolar.
    :param scroll_delay: Atraso entre cada rolagem.
    """
    for _ in range(num_scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        random_sleep(scroll_delay, scroll_delay * 1.5) # Pequeno atraso aleatório

def scroll_to_element(driver: WebDriver, element):
    """
    Rola a página até que o elemento esteja visível.
    :param driver: Instância do WebDriver.
    :param element: O elemento Selenium para rolar até.
    """
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    random_sleep(0.5, 1.5) # Pequeno atraso após rolar