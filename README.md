# 🏁 Melhor-Rota

**Melhor-Rota** é uma solução de automação robusta desenvolvida para otimizar o planejamento de rotas no Google Maps. Este projeto utiliza técnicas avançadas de automação web para inserir múltiplos destinos de forma ágil e eficiente, facilitando o gerenciamento de roteiros logísticos.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando o estado da arte em automação e scripting com Python:

- **[Python](https://www.python.org/)**: Linguagem base para toda a lógica e estruturação do script.
- **[Selenium](https://www.selenium.dev/)**: Framework principal para automação de navegadores, permitindo a interação direta com o Google Maps.
- **[Webdriver-Manager](https://pypi.org/project/webdriver-manager/)**: Gerenciamento automatizado de binários do navegador (ChromeDriver), garantindo compatibilidade e facilidade de configuração.
- **XPATH & DOM**: Utilizados para localização precisa de elementos dinâmicos na interface do Google Maps.

## 🧠 Conceitos Trabalhados

Durante o desenvolvimento deste projeto, explorei e apliquei diversos conceitos fundamentais de engenharia de software e automação:

- **Modularização de Código**: Implementação de funções especializadas que chamam outras funções (`função que chama função`), promovendo a reutilização e facilitando a manutenção.
- **Estratégias de Espera (Waits)**: Uso de `WebDriverWait` e `Expected Conditions` para lidar com o carregamento assíncrono de elementos web, tornando a automação muito mais resiliente.
- **Lógica de Controle de Estado**: Funções inteligentes que detectam se o menu de rotas está aberto ou fechado antes de prosseguir com a inserção de endereços.
- **Automação de Entrada de Usuário**: Simulação complexa de teclados (`Keys.CONTROL + "a"`, `Keys.RETURN`) para manipulação de campos de busca.

## 🚀 Experiências Obtidas

Desenvolver o **Melhor-Rota** foi uma jornada de aprendizado contínuo que me proporcionou experiências valiosas:

1.  **Resiliência em Automação**: Aprendi que automação web requer mais do que apenas encontrar botões; é sobre entender o ciclo de vida da página e lidar com latências de rede e carregamentos dinâmicos de forma elegante.
2.  **Engenharia de Selectors**: Aprimorei minhas habilidades em construir XPATHs robustos e flexíveis, capazes de resistir a mudanças sutis na estrutura do DOM do Google Maps.
3.  **Pensamento Modular**: A transição de um script linear para uma estrutura baseada em funções me ensinou a projetar código mais limpo e testável.
4.  **Resolução de Problemas Práticos**: O desafio de adicionar destinos dinamicamente no Maps me forçou a pensar em como o usuário interage com a interface e como replicar isso programaticamente com precisão.

---

*Desenvolvido com curiosidade e dedicação para facilitar processos logísticos.*