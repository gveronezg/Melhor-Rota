from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

# Configuração do Selenium
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(3)

# Acessar o site
driver.get("https://www.google.com/maps")

def rotas_abertas():
    xpath = '//button[@aria-label="Fechar rotas"]'
    botao_fechar_rotas = driver.find_elements(By.XPATH, xpath)
    return len(botao_fechar_rotas) > 0

def adiciona_destino(endereco, numero_caixas=1):
    if not rotas_abertas():
        # Aqui estamos selecionando o campo de busca
        campo_de_busca = driver.find_element(By.NAME, "q")
        # Aqui estamos digitando o endereço no campo de busca
        campo_de_busca.send_keys(endereco)
        # Aqui estamos pressionando Enter para buscar
        campo_de_busca.send_keys(Keys.RETURN)
    else:
        xpath = '//div[contains(@id, "directions-searchbox")]//input'
        caixas = driver.find_elements(By.XPATH, xpath)
        caixas = [c for c in caixas if c.is_displayed()]
        if len(caixas) >= numero_caixas:
            caixa_endereco = caixas[numero_caixas - 1]
            caixa_endereco.send_keys(Keys.CONTROL + "a")
            caixa_endereco.send_keys(Keys.DELETE)
            caixa_endereco.send_keys(endereco)
            caixa_endereco.send_keys(Keys.RETURN)
        else:
            print(f"Não foi possível adicionar o endereço {len(caixas)} | {numero_caixas}")

    # Para encontrar este xpath exato, primeiro abrimos o inspecionar elemento no navegador clicando em f12, depois localizamos o elemento alvo, identificamos um atributo chave presente (directions-searchbox). Apertamos Ctrl+F e digitamos o atributo chave presente para encontrar o xpath exato. A partir dai construimos todos o restante do caminho do xpath = //div[contains(@id, "directions-searchbox")]//input
    xpath = '//div[contains(@id, "directions-searchbox")]//input'

def abre_rotas():
    # XPATH de rotas
    xpath = "/html/body/div[1]/div[2]/div[9]/div[8]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[1]/button"
    # Esperar o carregamento do botão de rotas
    wait = WebDriverWait(driver, timeout=2)
    # Esperar até que o botão de rotas esteja presente na página
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    # Clicar no botão de rotas
    botao_rotas.click()

def adicionar_outros_destinos():
    xpath = '//span[text()="Adicionar destino"]'
    wait = WebDriverWait(driver, timeout=2)
    wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    botao_adicionar_destino = driver.find_element(By.XPATH, xpath)
    botao_adicionar_destino.click()

def fecha_rotas():
    # XPATH de fechar rotas
    xpath_fechar_rotas = '//button[@aria-label="Fechar rotas"]'
    # Esperar o carregamento do botão de fechar rotas
    wait = WebDriverWait(driver, timeout=2)
    # Esperar até que o botão de fechar rotas esteja presente na página
    botao_fechar_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath_fechar_rotas)))
    # NÃO Clicar no botão de fechar rotas
    # botao_fechar_rotas.click()

if __name__ == "__main__":
    enderecos = [
        "Av. Alonso Y Alonso, 3071 - Prolongamento Jardim Paulista, Franca - SP, 14401-426", # SESC
        "R. Abílio Coutinho, 331 - São Joaquim, Franca - SP, 14406-355", # São Joaquim Hospital e Maternidade
        "Av. Pres. Vargas, 105 - Cidade Nova, Franca - SP, 14401-110", # Padaria Estrela
        "Av. Eufrásia Monteiro Petráglia, 900 - Prolongamento Jardim Dr. Antonio Petraglia, Franca - SP, 14409-160" # Unesp
    ]
    adiciona_destino(enderecos[0], 1)
    abre_rotas()
    adiciona_destino(enderecos[0], 1)
    adiciona_destino(enderecos[1], 2)
    adicionar_outros_destinos()
    adiciona_destino(enderecos[2], 3)
    adicionar_outros_destinos()
    adiciona_destino(enderecos[3], 4)

    fecha_rotas()

    # Mantém o navegador aberto por 10 minutos
    sleep(600)

    # Fechar o navegador
    driver.quit()