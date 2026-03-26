import pulp
import itertools
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

# Configuração do Selenium
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(5)
micro_pausa = 0.3

def abre_o_maps_pronto_para_medicao():
    driver.get("https://www.google.com/maps")
    sleep(micro_pausa) # Espera inicial de carga
    # Entra com o endereço START
    campo_de_busca = driver.find_element(By.NAME, "q")
    sleep(micro_pausa)
    campo_de_busca.send_keys("Franca, SP, Brasil")
    sleep(micro_pausa)
    # Aqui estamos pressionando Enter para buscar
    campo_de_busca.send_keys(Keys.RETURN)
    sleep(micro_pausa*3)
    # Vamos abrir as rotas para lançar os pares
    # XPATH de rotas
    xpath = "//button[@aria-label='Rotas']"
    # Esperar o carregamento do botão de rotas
    wait = WebDriverWait(driver, timeout=60)
    # Esperar até que o botão de rotas esteja presente na página
    botao_rotas = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    sleep(micro_pausa)
    # Clicar no botão de rotas
    botao_rotas.click()
    sleep(micro_pausa*3)

def selecionar_tipo_de_transporte(tipo_de_transporte="Motocicleta"):
    xpath = f'//button[@data-tooltip="{tipo_de_transporte}"]'
    wait = WebDriverWait(driver, timeout=60)
    botao_transporte = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    sleep(micro_pausa)
    botao_transporte.click()
    sleep(micro_pausa*3)

def retorna_tempo_total():
    try:
        # XPath agora aceita tanto 'min' quanto 'h' (horas)
        xpath = '//div[@data-trip-index="0"]//div[contains(text(),"min") or contains(text(),"h")]'
        # Usamos uma espera menor aqui pois o sleep(2) já deu o tempo inicial de carga
        wait = WebDriverWait(driver, 10)
        tempo_total = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        sleep(micro_pausa)
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
    except TimeoutException:
        print("Aviso: Tempo não encontrado para este par.")
        return None

def retorna_distancia_total():
    try:
        xpath = '//div[@data-trip-index="0"]//div[contains(text(),"km")]'
        wait = WebDriverWait(driver, 10)
        distancia_total = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        sleep(micro_pausa)
        # Limpeza robusta: remove " km", remove pontos de milhar e troca vírgula por ponto decimal
        texto_limpo = distancia_total.text.replace(" km", "").replace(".", "").replace(",", ".")
        return float(texto_limpo)
    except TimeoutException:
        print("Aviso: Distância não encontrada para este par.")
        return None

def medir_os_pares(enderecos):
    distancias_em_pares = {}
    tempos_em_pares = {}
    
    # Espera as caixas estarem prontas antes de começar
    xpath_input = '//div[contains(@id, "directions-searchbox")]//input'
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_input)))
    except TimeoutException:
        print("Erro: Caixas de busca não carregaram.")
        return {}, {}

    caixas = driver.find_elements(By.XPATH, xpath_input)
    
    for i in range(len(enderecos) - 1):
        # Origem
        caixas[0].send_keys(Keys.CONTROL + "a")
        sleep(micro_pausa)
        caixas[0].send_keys(Keys.DELETE)
        sleep(micro_pausa)
        caixas[0].send_keys(enderecos[i])
        sleep(micro_pausa)
        caixas[0].send_keys(Keys.RETURN)
        
        caixas[1].send_keys(Keys.CONTROL + "a")
        sleep(micro_pausa)
        caixas[1].send_keys(Keys.DELETE)
        
        # Pausa para o Maps processar a troca de origem
        sleep(micro_pausa*3)

        for j in range(i + 1, len(enderecos)):
            caixas[1].send_keys(Keys.CONTROL + "a")
            sleep(micro_pausa)
            caixas[1].send_keys(Keys.DELETE)
            sleep(micro_pausa)
            caixas[1].send_keys(enderecos[j])
            sleep(micro_pausa)
            caixas[1].send_keys(Keys.RETURN)
            
            # Pausa para o cálculo da rota
            sleep(micro_pausa*3)
            
            tempo_par = retorna_tempo_total()
            distancia_par = retorna_distancia_total()
            
            tempos_em_pares[f'{i} -> {j}'] = tempo_par
            distancias_em_pares[f'{i} -> {j}'] = distancia_par

    return tempos_em_pares, distancias_em_pares

def gera_otimizacao(enderecos, distancias_em_pares, tempos_em_pares, modo="distancia"):
    """
    Resolve o Problema do Caixeiro Viajante (TSP) usando PuLP.
    modo: "distancia" ou "tempo"
    """
    def custo(i, j):
        # Tenta buscar i->j ou o espelho j->i
        chave = f'{i} -> {j}'
        chave_espelhada = f'{j} -> {i}'
        
        if modo == "distancia":
            val = distancias_em_pares.get(chave) or distancias_em_pares.get(chave_espelhada)
        else:
            val = tempos_em_pares.get(chave) or tempos_em_pares.get(chave_espelhada)
            
        return val if val is not None else 999999 # Penalidade para rota inválida

    n = len(enderecos)
    prob = pulp.LpProblem("Melhor_Rota_TSP", pulp.LpMinimize)
    
    # Variáveis de decisão: i para j (binário)
    x = pulp.LpVariable.dicts("x", [(i, j) for i in range(n) for j in range(n) if i != j], cat="Binary")
    
    # Função Objetivo: Minimizar a soma de todos os custos
    prob += pulp.lpSum([custo(i, j) * x[(i, j)] for i in range(n) for j in range(n) if i != j])
    
    # Restrições de entrada e saída (cada ponto deve ser visitado exatamente uma vez)
    for i in range(n):
        prob += pulp.lpSum([x[(i, j)] for j in range(n) if i != j]) == 1
        prob += pulp.lpSum([x[(j, i)] for j in range(n) if i != j]) == 1
    
    # Eliminação de sub-rotas (Subtour elimination)
    for k in range(n):
        for S in range(2, n):
            for subset in itertools.combinations([i for i in range(n) if i != k], S):
                prob += pulp.lpSum([x[(i, j)] for i in subset for j in subset if i != j]) <= len(subset) - 1

    # Silencia o PuLP e resolve
    print(f"\nOtimizando trajeto com foco em: {modo}...")
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    if pulp.LpStatus[prob.status] != 'Optimal':
        print("Erro: Não foi possível calcular a rota ideal.")
        return []

    # Reconstruindo a ordem do roteiro
    solucao = []
    atual = 0
    while True:
        for j in range(n):
            # Se o solver escolheu ir de 'atual' para 'j', adicionamos à lista
            if j != atual and x[(atual, j)].value() == 1:
                solucao.append((atual, j))
                atual = j
                break
        if atual == 0: # Voltamos ao ponto de partida
            break
            
    return solucao

def construir_rota_ideal():
    
if __name__ == "__main__":
    enderecos = [
        "R. Frankilim José Peres, 610 - Vila Exposicao, Franca - SP, 14405-451", # Casa
        "Av. Alonso Y Alonso, 3071 - Prolongamento Jardim Paulista, Franca - SP, 14401-426", # SESC
        "R. Abílio Coutinho, 331 - São Joaquim, Franca - SP, 14406-355", # São Joaquim Hospital e Maternidade
        "Av. Pres. Vargas, 105 - Cidade Nova, Franca - SP, 14401-110", # Padaria Estrela
        "Av. Eufrásia Monteiro Petráglia, 900 - Prolongamento Jardim Dr. Antonio Petraglia, Franca - SP, 14409-160" # Unesp
    ]

    try:
        abre_o_maps_pronto_para_medicao()
        selecionar_tipo_de_transporte("Motocicleta")
        
        # Coleta os dados
        minutos_em_pares, kms_em_pares = medir_os_pares(enderecos)
        
        print("\n--- Resultados (Tempo em Minutos) ---")
        print(minutos_em_pares)
        print("\n--- Resultados (Distância em KM) ---")
        print(kms_em_pares)

        ordem_otimizada = gera_otimizacao(enderecos, kms_em_pares, minutos_em_pares, modo="distancia")
        print("Roteiro Sugerido (Menor Distância):")
        for orig, dest in ordem_otimizada:
            print(f"De: {orig} -> {dest}\n")

        ordem_otimizada = gera_otimizacao(enderecos, kms_em_pares, minutos_em_pares, modo="tempo")
        print("Roteiro Sugerido (Menor Tempo):")
        for orig, dest in ordem_otimizada:
            print(f"De: {orig} -> {dest}\n")
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        print("\nFinalizando em 5 segundos...")
        sleep(5)
        driver.quit()