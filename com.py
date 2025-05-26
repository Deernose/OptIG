# com.py

import os
from selenium.webdriver.common.by import By

def salvar_comentarios(driver, usuario):
    try:
        # Extrai autor e legenda principais
        main_user = driver.find_element(By.XPATH, "//article//header//a[following-sibling::time]").text
        main_text = driver.find_element(By.XPATH, "//article//header/following-sibling::div//span[not(contains(@style,'line-height'))]").text

        comentarios = [f"{main_user}\n{main_text}\n"]

        # Blocos de comentários (lista de <li> dentro do artigo)
        comment_blocks = driver.find_elements(By.XPATH, "//article//ul[contains(@role,'list')]//li")
        for block in comment_blocks:
            try:
                # Ignora comentários de usuários verificados
                if block.find_elements(By.XPATH, ".//h3/*[name()='svg' and @aria-label='Verified']"):
                    continue
                user = block.find_element(By.XPATH, ".//h3/a").text
                text = block.find_element(By.XPATH, ".//h3/following-sibling::span[1]").text
                comentarios.append(f"{user}\n{text}\n")
            except:
                continue

        if comentarios:
            os.makedirs("leads", exist_ok=True)
            with open(f"leads/{usuario}.txt", "a", encoding="utf-8") as f:
                for comentario in comentarios:
                    f.write(comentario + "\n")
            print(f"[Salvo] Comentários de {usuario} atualizados.")
        else:
            print(f"[Info] Nenhum comentário encontrado para {usuario}.")
    except Exception as e:
        print(f"[Erro] Não foi possível salvar comentários de {usuario}: {e}")
