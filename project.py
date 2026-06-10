import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

headers = {"User-Agent": "Mozilla/5.0"}

base_url = "https://myanimelist.net/topmanga.php?limit="
data = []

print("Iniciando coleta...\n")


# -------------------------
# UTILITÁRIOS
# -------------------------

def clean(text):
    """Remove espaços extras, quebras de linha e caracteres duplicados."""
    if text:
        return text.strip().replace("\n", " ").replace("  ", " ")
    return None


# -------------------------
# SCRAPING DA PÁGINA INDIVIDUAL
# Captura somente o campo STATUS de cada obra
# -------------------------

def scrape_manga_page(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception:
        return {"status": None}

    info = {"status": None}

    for span in soup.select("span.dark_text"):
        label = span.text.strip()
        value = span.next_sibling

        if not value:
            continue

        value = clean(str(value))

        if "Status:" in label:
            info["status"] = value

    return info


# ThreadPoolExecutor: 10 workers em paralelo para acelerar a captura de status
executor = ThreadPoolExecutor(max_workers=10)


# -------------------------
# ETAPA 1 — COLETA BRUTA (ranking geral)
# Percorre as 20 páginas do Top Manga (50 obras por página = 1.000 registros)
# -------------------------

for i in range(0, 1000, 50):
    url = base_url + str(i)
    print(f"Coletando: {url}")

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("tr.ranking-list")

    for row in rows:
        title    = row.select_one("h3.manga_h3").text.strip()
        page_url = row.select_one("h3.manga_h3 a")["href"]

        # SCORE
        score_tag = row.select_one("td.score span")
        score     = score_tag.text.strip()
        score     = float(score) if score != "N/A" else None

        # INFO BOX (texto bruto com tipo, volumes e membros)
        info_box = row.select_one("div.information").text.strip()

        # TYPE — primeiro token antes do parêntese
        type_match = re.search(r"^(.+?)\s\(", info_box)
        type_      = type_match.group(1).strip() if type_match else None

        # MEMBERS
        mem_match = re.search(r"([\d,]+)\s*members", info_box)
        members   = int(mem_match.group(1).replace(",", "")) if mem_match else None

        # VOLUMES — "?" quando não informado (tratado no ETL)
        vols_match = re.search(r"(\d+)\s*vols", info_box)
        volumes    = int(vols_match.group(1)) if vols_match else "?"

        # Disparar scraping da página individual de forma assíncrona
        future = executor.submit(scrape_manga_page, page_url)

        data.append({
            "title":   title,
            "score":   score,
            "members": members,
            "volumes": volumes,
            "type":    type_,
            "_future": future,
        })

    time.sleep(0.3) 

# -------------------------
# ETAPA 2 — SINCRONIZAÇÃO DOS RESULTADOS DE STATUS
# Aguarda todas as threads e incorpora o campo status
# -------------------------

print("\nSincronizando resultados de STATUS...")

for item in data:
    f       = item.pop("_future")
    details = f.result()
    item.update(details)

executor.shutdown(wait=False)

# -------------------------
# DATAFRAME BRUTO
# -------------------------

df_before = pd.DataFrame(data)

print(f"\nRegistros brutos coletados: {len(df_before)}")

# -------------------------
# ETAPA 3 — LIMPEZA E TRANSFORMAÇÃO (ETL)
# -------------------------

# 3.1 Converter volumes: "?" → NaN para análise numérica
df_before["volumes_num"] = pd.to_numeric(df_before["volumes"], errors="coerce")

# 3.2 Remover duplicatas pelo título
df_after = df_before.drop_duplicates(subset=["title"])

# 3.3 Remover registros sem score ou members (campos críticos)
df_after = df_after.dropna(subset=["score", "members"])

print(f"Registros após remoção de duplicatas e nulos críticos: {len(df_after)}")

# -------------------------
# SALVAR CSV
# Nota: o CSV é salvo com df_after (inclui registros com volumes_num = NaN),
# pois o dashboard exibe todos os mangás e faz o dropna internamente
# apenas no Gráfico 5 (Histograma de Volumes).
# O script tecnica.py faz seu próprio dropna antes de treinar o modelo.
# -------------------------

df_after.to_csv("manga_dataset.csv", index=False)

print(f"\nDataset salvo como 'manga_dataset.csv' com {len(df_after)} registros.")
print(f"  → Registros com volumes informados : {df_after['volumes_num'].notna().sum()}")
print(f"  → Registros com volumes ausentes   : {df_after['volumes_num'].isna().sum()}")

# -------------------------
# ETAPA 4 — VALIDAÇÃO VISUAL (ETL)
# Comparação da distribuição de volumes antes e depois da limpeza
# Usado apenas para validação interna, não compõe o dashboard
# -------------------------

df_after_clean = df_after.dropna(subset=["volumes_num"])

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(df_before["volumes_num"].dropna(), bins=30, color="steelblue", edgecolor="white")
axes[0].set_title("Volumes — ANTES da limpeza")
axes[0].set_xlabel("Número de volumes")
axes[0].set_ylabel("Frequência")

axes[1].hist(df_after_clean["volumes_num"], bins=30, color="seagreen", edgecolor="white")
axes[1].set_title("Volumes — DEPOIS da limpeza")
axes[1].set_xlabel("Número de volumes")
axes[1].set_ylabel("Frequência")

plt.suptitle("Validação ETL — Distribuição de volumes antes e depois da limpeza")
plt.tight_layout()
plt.savefig("etl_volumes_validacao.png", dpi=150)
plt.show()

print("\nGráfico de validação ETL salvo como 'etl_volumes_validacao.png'")
print("\nColeta e ETL finalizados com sucesso.")
