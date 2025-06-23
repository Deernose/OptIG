from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import random
import time

from modules.utils import log_message, random_sleep, scroll_down

def navigate_reels(driver: WebDriver, user_config: dict):
    """
    Navega para a seção de Reels, rola, curte e tenta acessar os comentários.
    """
    min_delay = user_config['min_delay']
    max_delay = user_config['max_delay']

    log_message('info', "Iniciando navegação nos Reels.")
    
    try:
        # Tentar ir para a URL de Reels diretamente
        driver.get("https://www.instagram.com/reels/")
        log_message('info', "Acessando a página de Reels.")
        random_sleep(max_delay, max_delay * 1.5) # Espera maior para carregar a página de Reels

        # Tentar fechar pop-up de "Ativar notificações" novamente, se aparecer
        try:
            notif_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Agora não']"))
            )
            if notif_button:
                notif_button.click()
                log_message('info', "Clicou em 'Agora não' para notificações em Reels.")
                random_sleep(1, 2)
        except TimeoutException:
            log_message('info', "Pop-up de notificações não encontrado na página de Reels.")
        except ElementClickInterceptedException:
            log_message('warning', "Botão de notificação interceptado por outro elemento.")
            # Tentar um clique mais robusto ou ignorar
            pass # Vamos tentar continuar se for interceptado, pode ser uma pequena sobreposição

        # Rolar por alguns Reels antes de interagir
        num_scrolls_initial = random.randint(3, 7) # Rolar 3 a 7 vezes inicialmente
        log_message('info', f"Rolando {num_scrolls_initial} vezes para simular navegação inicial.")
        scroll_down(driver, num_scrolls_initial, 1.0) # Atraso de 1 segundo por rolagem

        # Loop para interagir com Reels
        num_reels_to_interact = random.randint(5, 10) # Interagir com 5 a 10 Reels por sessão
        log_message('info', f"Planejando interagir com {num_reels_to_interact} Reels.")

        for i in range(num_reels_to_interact):
            log_message('info', f"Processando Reel {i+1}/{num_reels_to_interact}...")
            random_sleep(min_delay, max_delay) # Pequeno atraso antes de cada interação com Reel

            # Tentar encontrar o botão de curtir (coração)
            # O Instagram usa SVG ou classes dinâmicas, então XPath por aria-label ou estrutura é melhor.
            # Exemplo de XPath para botão de curtir:
            # Procure por um botão dentro de um 'div' com um 'svg' que tenha um 'aria-label' de "Curtir" ou similar.
            # Este XPath pode precisar de ajustes dependendo da versão do layout do Instagram.
            like_button_xpath = "//*[name()='svg' and @aria-label='Curtir']/parent::*/parent::button"
            # Uma alternativa mais robusta pode ser procurar pelo elemento 'Curtir' e depois seu pai botão
            # //*[@aria-label='Curtir']

            try:
                like_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, like_button_xpath))
                )
                like_button.click()
                log_message('info', "Reel curtido.")
                random_sleep(1, 3) # Atraso após curtir
            except TimeoutException:
                log_message('warning', "Botão de curtir não encontrado ou não clicável para o Reel atual. Pulando curtir.")
            except ElementClickInterceptedException:
                log_message('warning', "Clique no botão de curtir interceptado. Tentando novamente ou pulando.")
                # Tentar rolar um pouco ou aguardar e tentar novamente
                random_sleep(1, 2)
                try:
                    like_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, like_button_xpath))
                    )
                    like_button.click()
                    log_message('info', "Reel curtido após re-tentativa.")
                except:
                    log_message('warning', "Re-tentativa de curtir falhou. Pulando curtir.")
            except NoSuchElementException:
                log_message('warning', "Elemento do botão de curtir não encontrado no DOM. Pulando curtir.")

            # Acessar comentários
            comment_button_xpath = "//*[name()='svg' and @aria-label='Comentar']/parent::*/parent::button"
            try:
                comment_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, comment_button_xpath))
                )
                comment_button.click()
                log_message('info', "Acessando comentários do Reel.")
                random_sleep(min_delay, max_delay) # Espera para carregar os comentários
                
                # TODO: Aqui chamaríamos o módulo comments_and_ai.py para coletar/analisar/comentar
                # Por agora, apenas demonstramos o acesso.
                
                # Voltar ao Reel ou fechar a seção de comentários
                # Geralmente há um botão de "fechar" ou "voltar"
                close_comment_xpath = "//*[name()='svg' and @aria-label='Fechar']/parent::button"
                try:
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, close_comment_xpath))
                    )
                    close_button.click()
                    log_message('info', "Fechando seção de comentários.")
                    random_sleep(1, 2)
                except TimeoutException:
                    log_message('warning', "Botão de fechar comentários não encontrado. Tentando ESC ou ignorando.")
                    # Pode tentar simular a tecla ESC para fechar
                    # from selenium.webdriver.common.keys import Keys
                    # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    pass
                
            except TimeoutException:
                log_message('warning', "Botão de comentários não encontrado ou não clicável para o Reel atual. Pulando comentários.")
            except ElementClickInterceptedException:
                log_message('warning', "Clique no botão de comentários interceptado. Pulando comentários.")
            except NoSuchElementException:
                log_message('warning', "Elemento do botão de comentários não encontrado no DOM. Pulando comentários.")

            # Rolar para o próximo Reel
            # O Instagram carrega os Reels conforme você rola.
            # Uma rolagem simples para baixo geralmente carrega o próximo.
            log_message('info', "Rolando para o próximo Reel...")
            scroll_down(driver, 1, 0.5) # Rola apenas uma vez para o próximo Reel
            random_sleep(min_delay, max_delay) # Atraso após rolagem

    except Exception as e:
        log_message('error', f"Erro geral na navegação de Reels: {e}")