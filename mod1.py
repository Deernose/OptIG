import time
import random
import subprocess
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)


def func1(driver, max_delay_minutos=5):
    """
    Percorre a lista de usuários, abre cada perfil e
    chama seguir_curtidores em cada post encontrado.
    Entre cada post (exceto o primeiro), executa del.py como subprocesso.
    """
    usuarios = carregar_usuarios()
    if not usuarios:
        usuarios = entrada_usuarios_manual()

    for usuario in usuarios:
        print(f"[Abrindo perfil] https://www.instagram.com/{usuario}/")
        driver.get(f"https://www.instagram.com/{usuario}/")

        try:
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main[role='main']")))

            anchors = wait.until(EC.presence_of_all_elements_located((
                By.XPATH, "//main//a[contains(@href,'/p/')]")
            ))
            posts_links = [a.get_attribute("href") for a in anchors]
            print(f"[Depuração] {len(posts_links)} posts encontrados para {usuario}")

            for idx, post_url in enumerate(posts_links):
                # Executa del.py antes de cada post, exceto o primeiro
                if idx > 0:
                    print("[Delay] Executando script de engajamento (del.py)...")
                    try:
                        subprocess.run([sys.executable, "del.py"], check=True)
                        print("[Delay] del.py concluído. Retomando mod1.py.")
                    except subprocess.CalledProcessError as e:
                        print(f"[Aviso] del.py retornou código {e.returncode}, prosseguindo sem delay extra.")

                print(f"[Processando post] {idx+1}/{len(posts_links)}: {post_url}")
                driver.get(post_url)
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "article")))
                time.sleep(2)
                seguir_curtidores(driver, max_delay_minutos)

        except Exception as e:
            print(f"[Erro] ao abrir perfil {usuario}: {e}")


def seguir_curtidores(driver, max_delay_minutos):
    """
    Abre a lista de curtidores de um post e clica em uma quantidade
    fixa de 1 usuário para teste, depois retorna.
    """
    try:
        wait = WebDriverWait(driver, 10)

        like_links = driver.find_elements(By.XPATH, "//a[contains(@href,'/liked_by/')]")
        for link in reversed(like_links):
            if link.is_displayed():
                link.click()
                print("[Ação] Abriu lista de curtidores.")
                break
        else:
            print("[Erro] Botão de curtidores não encontrado.")
            return

        time.sleep(2)

        scroll_box = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//div[@role='dialog']//div[contains(@style,'overflow')]")
        ))
        last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
            time.sleep(1)
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
            if new_height == last_height:
                break
            last_height = new_height

        # Ajusta XPath usando 'or' para múltiplos textos
        follow_buttons = scroll_box.find_elements(
            By.XPATH,
            ".//button[.//div[@dir='auto' and normalize-space(text())='Follow'] or .//div[@dir='auto' and normalize-space(text())='Seguir']]"
        )
        total = len(follow_buttons)
        to_click = 1  # teste fixo
        print(f"[Depuração] {total} botões encontrados, seguindo {to_click}.")

        for btn in follow_buttons[:to_click]:
            try:
                btn.click()
                print("[Ação] Seguiu um usuário.")
                random_delay(1, max_delay_minutos * 60)
            except (ElementClickInterceptedException, StaleElementReferenceException):
                continue

    except TimeoutException:
        print("[Erro] Timeout ao abrir lista de curtidores ou localizar elementos.")
    except Exception as e:
        print(f"[Erro] Falha no seguir_curtidores: {e}")


def random_delay(min_seconds, max_seconds):
    delay = random.uniform(min_seconds, max_seconds)
    print(f"[Espera] Aguardando {int(delay)} segundos...")
    time.sleep(delay)


def carregar_usuarios():
    try:
        with open("lista.txt", "r", encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print("Arquivo lista.txt não encontrado.")
        return []


def entrada_usuarios_manual():
    print("="*40)
    print("Digite nomes de usuários (vírgula ou espaço). '!' para terminar.")
    print("="*40)
    usuarios = []
    blank = 0
    while True:
        txt = input("Usuários: ").strip()
        if txt == "!":
            break
        if not txt:
            blank += 1
            if blank >= 3:
                break
            continue
        blank = 0
        usuarios.extend(parse_usuarios(txt))
    return [u for u in usuarios if u]


def parse_usuarios(texto):
    if ',' in texto:
        return [p.strip() for p in texto.split(',') if p.strip()]
    return texto.split()


if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    chrome_driver_path = r"C:\Temp\chromedriver.exe"
    debug_port = 9222

    options = Options()
    options.debugger_address = f"127.0.0.1:{debug_port}"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    max_delay_minutos = 5
    func1(driver, max_delay_minutos)
    driver.quit()
