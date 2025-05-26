import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)


def func1(driver, max_delay_minutos=5):
    """
    Percorre a lista de usuários, abre cada perfil e
    chama seguir_curtidores em cada post encontrado.
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

            # espera e coleta links de posts
            anchors = wait.until(EC.presence_of_all_elements_located((
                By.XPATH, "//main//a[contains(@href,'/p/')]")
            ))
            posts_links = [a.get_attribute("href") for a in anchors]
            print(f"[Depuração] {len(posts_links)} posts encontrados para {usuario}")

            for post_url in posts_links:
                try:
                    driver.get(post_url)
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "article")))
                    time.sleep(2)
                    seguir_curtidores(driver, max_delay_minutos)
                except Exception as e:
                    print(f"[Erro] ao processar post {post_url}: {e}")

        except Exception as e:
            print(f"[Erro] ao abrir perfil {usuario}: {e}")


def seguir_curtidores(driver, max_delay_minutos):
    """
    Abre a lista de curtidores de um post e clica
    em todos os botões 'Seguir' ou 'Follow'.
    """
    try:
        wait = WebDriverWait(driver, 10)

        # 1) Encontra e clica no link de curtidores
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

        # 2) Localiza o container rolável dentro do modal
        scroll_box = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//div[@role='dialog']//div[contains(@style,'overflow')]"
        )))

        # 3) Rola até o fim para carregar todos os itens
        last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
            time.sleep(1)
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
            if new_height == last_height:
                break
            last_height = new_height

        # 4) Coleta e clica botões de seguir focando no atributo dir e texto
        follow_buttons = scroll_box.find_elements(
            By.XPATH,
            (
                ".//button[.//div[@dir='auto' and normalize-space(text())='Follow']]"
                "|.//button[.//div[@dir='auto' and normalize-space(text())='Seguir']]"
            )
        )
        print(f"[Depuração] {len(follow_buttons)} botões de seguir encontrados.")

        for btn in follow_buttons:
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
