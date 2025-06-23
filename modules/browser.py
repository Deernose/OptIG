import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import sys

# Importar utils para usar random_sleep e log_message
from modules.utils import random_sleep, log_message

def setup_browser(headless_mode: bool = False) -> webdriver.Chrome:
    """
    Configura e retorna uma instância do WebDriver Chrome com opções anti-detecção.
    """
    log_message('info', "Configurando o navegador...")
    chrome_options = Options()

    # --- Opções Anti-detecção ---
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")

    if headless_mode:
        chrome_options.add_argument("--headless=new")
        log_message('info', "Modo headless ativado.")

    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        log_message('info', "Navegador Chrome iniciado com sucesso.")
        return driver
    except WebDriverException as e:
        log_message('error', f"Erro ao iniciar o WebDriver: {e}")
        log_message('error', "Certifique-se de que o ChromeDriver está instalado e no PATH, ou especifique o caminho manualmente.")
        sys.exit(1)

def wait_for_manual_login(driver: webdriver.Chrome):
    """
    Aguarda o usuário realizar o login manual no Instagram.
    """
    log_message('info', "Navegando para a página de login do Instagram. Por favor, faça o login manual.")
    driver.get("https://www.instagram.com/accounts/login/")

    # Pequena pausa para garantir que a página carregue antes de o usuário interagir
    random_sleep(5, 10)

    print("\n" + "="*50)
    print(" POR FAVOR, FAÇA O LOGIN MANUAL NO NAVEGADOR AGORA. ")
    print(" O bot continuará automaticamente APÓS o login ser detectado. ")
    print("="*50 + "\n")

    try:
        # Espera até que a URL mude para a página principal do Instagram ou um elemento pós-login apareça.
        # Elementos como o ícone de Direct Message são bons indicadores de login bem-sucedido.
        WebDriverWait(driver, 120).until( # Aumentamos o tempo limite para o login manual
            EC.url_to_be("https://www.instagram.com/") or
            EC.presence_of_element_located((By.XPATH, "//a[@href='/direct/inbox/']"))
        )
        log_message('info', "Login manual detectado com sucesso!")

        # Lidar com pop-up de "Salvar Informações" (ainda pode aparecer após login manual)
        try:
            not_now_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Agora não']"))
            )
            not_now_button.click()
            log_message('info', "Clicou em 'Agora não' para salvar informações de login.")
            random_sleep(1, 2)
        except TimeoutException:
            log_message('info', "Pop-up 'Salvar Informações' não encontrado.")

        # Lidar com pop-up de "Ativar Notificações"
        try:
            not_now_button_notification = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Agora não']"))
            )
            not_now_button_notification.click()
            log_message('info', "Clicou em 'Agora não' para ativar notificações.")
            random_sleep(1, 2)
        except TimeoutException:
            log_message('info', "Pop-up 'Ativar Notificações' não encontrado.")

    except TimeoutException:
        log_message('error', "Tempo limite excedido para o login manual. O bot não detectou o login.")
        driver.quit()
        sys.exit(1)
    except Exception as e:
        log_message('error', f"Ocorreu um erro inesperado durante a espera pelo login: {e}")
        driver.quit()
        sys.exit(1)