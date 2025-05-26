import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import socket
import sys

chrome_driver_path = r"C:\Temp\chromedriver.exe"
instagram_url = "https://www.instagram.com/"
debug_port = 9222
user_data_dir = r"C:\Temp\ChromeProfile"

def is_debug_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect(("127.0.0.1", port))
            return True
        except:
            return False

def start_chrome():
    chrome_cmd = [
        "start",
        "chrome.exe",
        f"--remote-debugging-port={debug_port}",
        f'--user-data-dir="{user_data_dir}"',
        instagram_url
    ]
    subprocess.Popen(" ".join(chrome_cmd), shell=True)
    time.sleep(5)

def pedir_tempo_maximo():
    print("="*50)
    print("Defina o tempo máximo de espera entre ações (em minutos).")
    print("Recomendado: 5 minutos para usuários novos.")
    print("Digite um número inteiro (ex: 5) ou pressione Enter para usar o padrão (5):")
    print("="*50)
    while True:
        entrada = input("Tempo máximo (minutos): ").strip()
        if entrada == "":
            return 5  # padrão
        if entrada.isdigit() and int(entrada) > 0:
            return int(entrada)
        else:
            print("Entrada inválida. Digite um número inteiro positivo ou Enter para padrão.")

def main():
    if not is_debug_port_open(debug_port):
        print("Chrome com depuração não está aberto. Iniciando...")
        start_chrome()
    else:
        print("Conectando ao Chrome já aberto...")

    options = Options()
    options.debugger_address = f"127.0.0.1:{debug_port}"
    service = Service(chrome_driver_path)

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        print("Erro ao conectar ao Chrome:", e)
        sys.exit(1)

    # Se já houver abas abertas, troca a aba ativa para Instagram inicial
    try:
        # Percorre todas as abas abertas
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if "instagram.com" in driver.current_url:
                driver.get(instagram_url)
                print("[Info] Página inicial do Instagram carregada na aba existente.")
                break
        else:
            # Se nenhuma aba Instagram aberta, abre nova aba com Instagram
            driver.execute_script(f"window.open('{instagram_url}');")
            driver.switch_to.window(driver.window_handles[-1])
            print("[Info] Nova aba aberta com página inicial do Instagram.")
    except Exception as e:
        print(f"[Erro] Ao garantir página inicial do Instagram: {e}")

    print("Faça login no navegador aberto e pressione Enter para continuar...")
    input()

    max_delay_minutos = pedir_tempo_maximo()
    print(f"Tempo máximo de espera configurado para {max_delay_minutos} minutos.")

    from mod1 import func1
    func1(driver, max_delay_minutos)

    driver.quit()

if __name__ == "__main__":
    main()
