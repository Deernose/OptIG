import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys


def process_reels_and_stories(driver):
    """
    Abre e visualiza 1 story (ignorando 'Your story'), curte com SVG aria-label='Like',
    depois executa reels e retorna ao feed.
    """
    wait = WebDriverWait(driver, 20)

    # 1. Stories: voltar à home e abrir primeiro story de outro usuário
    driver.get("https://www.instagram.com/")
    print("[Stories][Debug] Navegado para home para carregar stories.")
    time.sleep(5)

    try:
        print("[Stories] Tentando abrir 1 story de outro usuário...")
        # Localiza todos os botões de story
        story_buttons = wait.until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//div[@role='button' and contains(@aria-label, 'Story by')]"
            ))
        )
        # Filtra para ignorar o próprio 'Your story'
        btn_story = None
        for btn in story_buttons:
            try:
                text = btn.find_element(By.XPATH, ".//span[normalize-space(text())='Your story']").text
            except:
                # se não encontrar 'Your story', é válido
                btn_story = btn
                break
        if not btn_story:
            raise TimeoutException("Nenhum story disponível de outros usuários")

        driver.execute_script("arguments[0].scrollIntoView(true);", btn_story)
        time.sleep(1)
        try:
            btn_story.click()
            print("[Stories][Ação] Story aberto.")
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", btn_story)
            print("[Stories][Ação] Story aberto via JS.")

        # Aguarda carregamento do like
        time.sleep(3)
        like_svg = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "svg[aria-label='Like']"
            ))
        )

        # Clicar no botão de Like via SVG
        try:
            like_btn = like_svg.find_element(By.XPATH, "./ancestor::*[@role='button']")
            driver.execute_script("arguments[0].scrollIntoView(true);", like_btn)
            time.sleep(1)
            try:
                like_btn.click()
                print("[Stories][Ação] Story curtido.")
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", like_btn)
                print("[Stories][Ação] Story curtido via JS.")
            time.sleep(2)
        except Exception as e:
            print(f"[Stories][Erro] não conseguiu curtir story: {type(e).__name__}: {e}")

        # Fecha o story
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        print("[Stories][Debug] Story fechado.")
        time.sleep(1)

    except Exception as e:
        print(f"[Stories][Erro] {type(e).__name__}: {e}")

    # 2. Reels: executa a lógica de curtida de reels
    try:
        process_reels_and_stories_reels_only(driver)
    except Exception as e:
        print(f"[Reels][Erro] {type(e).__name__}: {e}")


def process_reels_and_stories_reels_only(driver):
    wait = WebDriverWait(driver, 20)
    reels_to_like = 1
    print(f"[Reels] Tentando curtir {reels_to_like} reel(s) via SVG aria-label='Like'...")
    driver.get("https://www.instagram.com/reels/")
    print("[Reels][Debug] /reels/ aberto.")
    time.sleep(5)

    like_svgs = wait.until(
        EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            "svg[aria-label='Like']"
        ))
    )
    print(f"[Reels][Debug] Encontrados {len(like_svgs)} SVG(s) com aria-label='Like'.")
    liked = 0
    for svg in like_svgs:
        if liked >= reels_to_like:
            break
        try:
            btn = svg.find_element(By.XPATH, "./ancestor::*[@role='button']")
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(1)
            try:
                btn.click()
                print(f"[Reels][Ação] Reel curtido ({liked+1}/{reels_to_like}).")
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", btn)
                print(f"[Reels][Ação] Reel curtido via JS ({liked+1}/{reels_to_like}).")
            liked += 1
            time.sleep(2)
        except Exception as e:
            print(f"[Reels][Erro] falha ao clicar SVG Like: {type(e).__name__}: {e}")
    if liked == 0:
        print("[Reels][Erro] Nenhum reel foi curtido.")
    driver.get("https://www.instagram.com/")
    print("[Reels][Debug] Retornado ao feed principal.")


if __name__ == '__main__':
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    chrome_driver_path = r"C:\Temp\chromedriver.exe"
    debug_port = 9222

    options = Options()
    options.debugger_address = f"127.0.0.1:{debug_port}"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    print("Iniciando interações de teste (1 story, 1 reel)...")
    process_reels_and_stories(driver)

    driver.quit()
