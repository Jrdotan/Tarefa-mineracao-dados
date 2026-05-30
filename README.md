# 📚 MyAnimeList Web Scraping & Data Mining

Este projeto foi desenvolvido no contexto da disciplina de **Mineração de Dados**, com o objetivo de realizar a **coleta, tratamento e análise exploratória de dados** a partir do ranking de mangás do **MyAnimeList**.

A base construída reúne informações relevantes sobre as obras listadas no ranking, permitindo aplicar etapas de **ETL**, gerar uma base estruturada em **CSV** e comparar a distribuição da variável relacionada ao número de volumes **antes e depois da limpeza**.

---

## 📌 Objetivo

- Coletar dados do ranking de mangás do MyAnimeList por meio de web scraping
- Estruturar os dados em formato tabular
- Aplicar etapas de ETL (Extract, Transform, Load)
- Realizar limpeza e pré-processamento
- Exportar uma base tratada para análises futuras
- Gerar visualizações comparativas da distribuição do número de volumes

---

## 🛠️ Tecnologias Utilizadas

- Python 
- Requests
- BeautifulSoup
- Pandas
- Matplotlib
- Regex (`re`)
- ThreadPoolExecutor
- RandomForest
- Streamlit

---

## 📊 Fonte de Dados

Os dados foram coletados a partir do ranking de mangás do MyAnimeList:

🔗 https://myanimelist.net/topmanga.php

### Informações extraídas
- Título da obra
- Pontuação
- Quantidade de membros
- Número de volumes
- Tipo da obra
- Status de publicação

### Escopo da coleta
- Leitura paginada do ranking
- Coleta de até 1.000 entradas da listagem
- Complementação de dados com acesso às páginas individuais de cada obra

---

## ⚙️ Pipeline ETL

O projeto segue um fluxo de ETL dividido em três etapas principais:

```text
Extração (Scraping)
        ↓
Coleta do ranking e das páginas individuais
        ↓
Estruturação inicial dos registros
        ↓
Tratamento e limpeza dos dados
        ↓
Criação da base final
        ↓
Exportação para CSV e visualização gráfica 

```
```
## Como executar
Instale as dependências:

bash
pip install -r requirements.txt

python project.py
python tecnica.py
streamlit run dashboard.py
```

