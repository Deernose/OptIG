import sys
import os
from typing import Dict, Any
from modules.browser import setup_browser, wait_for_manual_login
from modules.utils import log_message, random_sleep

# --- Importar as configurações do usuário ---
try:
    from user_config import CHROMEDRIVER_PATH, OPENAI_API_KEY
except ImportError:
    log_message('error', "Arquivo 'user_config.py' não encontrado. Crie-o seguindo o modelo.")
    sys.exit(1)

# --- Importar o módulo de Reels ---
from core_actions import reels # Importar o módulo reels

# --- Configurações e Perguntas Iniciais ---
def get_user_config() -> Dict[str, Any]:
    # ... (código existente para obter configurações) ...
    config: Dict[str, Any] = {}
    config_file_path = os.path.join("data", "pre_defined_answers.txt")

    if os.path.exists(config_file_path):
        log_message('info', f"Lendo configurações de '{config_file_path}'...")
        with open(config_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                config['speed'] = lines[0].strip().lower()
                config['keyword'] = lines[1].strip()
                log_message('info', f"Configurações lidas: Velocidade='{config['speed']}', Palavra-Chave='{config['keyword']}'")
            else:
                log_message('warning', "Arquivo 'pre_defined_answers.txt' não contém respostas suficientes. Solicitando ao usuário.")
    
    if 'speed' not in config:
        while True:
            speed_input = input("Defina a velocidade das ações (lenta, normal, rapida): ").strip().lower()
            if speed_input in ["lenta", "normal", "rapida"]:
                config['speed'] = speed_input
                break
            else:
                print("Entrada inválida. Por favor, digite 'lenta', 'normal' ou 'rapida'.")

    if 'keyword' not in config:
        config['keyword'] = input("Digite a palavra-chave principal (ex: CURSO): ").strip()

    if config['speed'] == 'lenta':
        config['min_delay'] = 5.0
        config['max_delay'] = 10.0
    elif config['speed'] == 'normal':
        config['min_delay'] = 3.0
        config['max_delay'] = 7.0
    elif config['speed'] == 'rapida':
        config['min_delay'] = 1.0
        config['max_delay'] = 4.0
    else: # Default para normal
        config['min_delay'] = 3.0
        config['max_delay'] = 7.0

    log_message('info', f"Atrasos configurados: Min={config['min_delay']}s, Max={config['max_delay']}s")
    return config


def main():
    log_message('info', "Iniciando OptIG Advanced...")

    user_config: Dict[str, Any] = get_user_config()
    driver = setup_browser(headless_mode=False) 

    if driver:
        wait_for_manual_login(driver)

    log_message('info', "Bot pronto! Iniciando ciclo de atividades...")
    try:
        while True:
            # Chamar a ação de Reels
            reels.navigate_reels(driver, user_config) # Adicionado aqui

            # TODO: Outras ações virão aqui (comentários, feed, stories)

            log_message('info', "Ciclo de atividades completo. Pausando para próximo ciclo...")
            random_sleep(user_config['max_delay'] * 5, user_config['max_delay'] * 10)

    except KeyboardInterrupt:
        log_message('info', "Bot interrompido pelo usuário.")
    except Exception as e:
        log_message('error', f"Um erro inesperado ocorreu no loop principal: {e}")
    finally:
        if driver:
            log_message('info', "Fechando o navegador.")
            driver.quit()
        log_message('info', "OptIG Advanced finalizado.")
        sys.exit(0)

if __name__ == "__main__":
    main()