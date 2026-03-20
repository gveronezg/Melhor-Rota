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

def adiciona_destino(endereco):
    # Aqui estamos selecionando o campo de busca
    campo_de_busca = driver.find_element(By.NAME, "q")
    # Aqui estamos digitando o endereço no campo de busca
    campo_de_busca.send_keys(endereco)
    # Aqui estamos pressionando Enter para buscar
    campo_de_busca.send_keys(Keys.RETURN)

def abre_rotas():
    # XPATH de rotas
    xpath = "/html/body/div[1]/div[2]/div[9]/div[8]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[1]/button"
    # Esperar o carregamento do botão de rotas
    wait = WebDriverWait(driver, timeout=2)
    # Esperar até que o botão de rotas esteja presente na página
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    # Clicar no botão de rotas
    botao_rotas.click()

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
    endereco = "Av. Alonso Y Alonso, 3071 - Prolongamento Jardim Paulista, Franca - SP, 14401-426" # SESC
    adiciona_destino(endereco)
    abre_rotas()
    fecha_rotas()

    # Mantém o navegador aberto por 10 minutos
    sleep(600)
    
    # Fechar o navegador
    driver.quit()