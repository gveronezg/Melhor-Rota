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
driver.implicitly_wait(5)

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
    wait = WebDriverWait(driver, timeout=60)
    # Esperar até que o botão de rotas esteja presente na página
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    # Clicar no botão de rotas
    botao_rotas.click()

def adicionar_outros_destinos():
    xpath = '//span[text()="Adicionar destino"]'
    wait = WebDriverWait(driver, timeout=60)
    wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    botao_adicionar_destino = driver.find_element(By.XPATH, xpath)
    botao_adicionar_destino.click()

def seleciona_tipo_de_transporte(tipo_de_transporte="Motocicleta"):
    xpath = f'//button[@data-tooltip="{tipo_de_transporte}"]'
    wait = WebDriverWait(driver, timeout=60)
    botao_transporte = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    botao_transporte.click()

def retorna_tempo_total():
    # XPath agora aceita tanto 'min' quanto 'h' (horas)
    xpath = '//div[@data-trip-index="0"]//div[contains(text(),"min") or contains(text(),"h")]'
    wait = WebDriverWait(driver, timeout=60)
    tempo_total = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    texto = tempo_total.text.lower().strip() # Ex: "1 h 20 min" ou "45 min"
    
    total_minutos = 0
    
    # Se houver "h" na string, extraímos as horas e multiplicamos por 60
    if "h" in texto:
        partes = texto.split("h")
        horas = int(partes[0].strip())
        total_minutos += horas * 60
        texto_restante = partes[1] # O que sobra depois do "h"
    else:
        texto_restante = texto
        
    # Se houver "min" no que restou (ou na string original), extraímos e somamos
    if "min" in texto_restante:
        minutos_str = texto_restante.replace("min", "").strip()
        if minutos_str:
            total_minutos += int(minutos_str)
            
    return int(total_minutos)

def retorna_distancia_total():
    xpath = '//div[@data-trip-index="0"]//div[contains(text(),"km")]'
    wait = WebDriverWait(driver, timeout=60)
    distancia_total = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    # Limpeza robusta: remove " km", remove pontos de milhar e troca vírgula por ponto decimal
    texto_limpo = distancia_total.text.replace(" km", "").replace(".", "").replace(",", ".")
    return float(texto_limpo)

##### FUNÇÕES PRINCIPAIS #####

def gera_pares_distancias_e_tempos(enderecos):
    distancias_em_pares = {}
    tempos_em_pares = {}
    driver.get("https://www.google.com/maps")
    adiciona_destino(enderecos[0], 1)
    abre_rotas()
    seleciona_tipo_de_transporte("Motocicleta")

    for i, end1 in enumerate(enderecos):
        adiciona_destino(end1, 1)
        sleep(1) # Estabiliza após trocar a origem
        for j, end2 in enumerate(enderecos):
            if i != j:
                adiciona_destino(end2, 2)
                sleep(2) # Pausa para o Maps calcular a nova rota
                tempo_par = retorna_tempo_total()
                tempos_em_pares[f'{i} -> {j}'] = tempo_par
                distancia_par = retorna_distancia_total()
                distancias_em_pares[f'{i} -> {j}'] = distancia_par

    return distancias_em_pares, tempos_em_pares

if __name__ == "__main__":
    enderecos = [
        "Av. Alonso Y Alonso, 3071 - Prolongamento Jardim Paulista, Franca - SP, 14401-426", # SESC
        "R. Abílio Coutinho, 331 - São Joaquim, Franca - SP, 14406-355", # São Joaquim Hospital e Maternidade
        "Av. Pres. Vargas, 105 - Cidade Nova, Franca - SP, 14401-110", # Padaria Estrela
        "Av. Eufrásia Monteiro Petráglia, 900 - Prolongamento Jardim Dr. Antonio Petraglia, Franca - SP, 14409-160" # Unesp
    ]

    distancias_em_pares, tempos_em_pares = gera_pares_distancias_e_tempos(enderecos)
    print(distancias_em_pares)
    print(tempos_em_pares)

    # Mantém o navegador aberto por 10 minutos
    sleep(600)

    # Fechar o navegador
    driver.quit()