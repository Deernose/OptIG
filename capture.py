import subprocess
import time
import socket
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Configuration
chrome_driver_path = r"C:\Temp\chromedriver.exe"
debug_port = 9222
user_data_dir = r"C:\Temp\ChromeProfile"
instagram_url = "https://www.instagram.com/"


def is_debug_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect(("127.0.0.1", port))
            return True
        except:
            return False


def start_chrome():
    cmd = [
        "start",
        "chrome.exe",
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={user_data_dir}",
        instagram_url
    ]
    subprocess.Popen(" ".join(cmd), shell=True)
    time.sleep(5)


def main():
    # Launch or connect to Chrome
    if not is_debug_port_open(debug_port):
        print("Chrome com depuração não está aberto. Iniciando...")
        start_chrome()
    else:
        print("Conectando ao Chrome já aberto...")

    options = Options()
    options.debugger_address = f"127.0.0.1:{debug_port}"
    # Enable browser console logging
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    service = Service(chrome_driver_path)

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        print("Erro ao conectar ao Chrome:", e)
        sys.exit(1)

    # Focus on Instagram tab or open new one
    try:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if "instagram.com" in driver.current_url:
                driver.get(instagram_url)
                break
        else:
            driver.execute_script(f"window.open('{instagram_url}');")
            driver.switch_to.window(driver.window_handles[-1])
    except Exception as e:
        print(f"Erro ao abrir Instagram: {e}")

    input("Faça login no Instagram no navegador e pressione Enter para continuar...")

    # Inject click listener
    js_listener = r"""
    (function(){
      document.addEventListener('click', function(e){
        const info = {
          tag: e.target.tagName,
          classes: e.target.className,
          aria: e.target.getAttribute('aria-label') || null,
          text: (e.target.innerText || '').slice(0,50)
        };
        console.log('CLICK:' + JSON.stringify(info));
      }, true);
    })();
    """
    driver.execute_script(js_listener)
    print("Listener de cliques injetado. Agora clique nos elementos e acompanhe os logs abaixo:")

    # Poll console logs
    try:
        while True:
            time.sleep(1)
            for entry in driver.get_log('browser'):
                msg = entry.get('message')
                if 'CLICK:' in msg:
                    # Extract JSON payload
                    try:
                        payload = msg.split('CLICK:')[1]
                        print("[CLICK]", payload)
                    except:
                        print("[CLICK]", msg)
    except KeyboardInterrupt:
        print("Interrupção recebida. Encerrando...")
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
