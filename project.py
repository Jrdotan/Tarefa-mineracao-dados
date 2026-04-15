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

#limpando textos
def clean(text):
    if text:
        return text.strip().replace("\n", " ").replace("  ", " ")
    return None


#scrap individual (somente status)
def scrape_manga_page(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
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


executor = ThreadPoolExecutor(max_workers=10)

# extracao (etapa 1 - raw)
for i in range(0, 1000, 50):
    url = base_url + str(i)
    print("Coletando:", url)
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    rows = soup.select("tr.ranking-list")

    for row in rows:
        title = row.select_one("h3.manga_h3").text.strip()
        page_url = row.select_one("h3.manga_h3 a")["href"]
        
        #localiza score
        score_tag = row.select_one("td.score span")
        score = score_tag.text.strip()
        score = float(score) if score != "N/A" else None
        
        #guarda box de informacoes (raw)
        info_box = row.select_one("div.information").text.strip()
        
        #extracao com regex RE
        type_match = re.search(r"^(.+?)\s\(", info_box)
        type_ = type_match.group(1).strip() if type_match else None
        
        #membros
        mem_match = re.search(r"([\d,]+)\s*members", info_box)
        members = int(mem_match.group(1).replace(",", "")) if mem_match else None
        
        #procura volumes (trata: ? se nulo)
        vols_match = re.search(r"(\d+)\s*vols", info_box)
        if vols_match:
            volumes = int(vols_match.group(1))
        else:
            volumes = "?"
            
        future = executor.submit(scrape_manga_page, page_url)
        
        data.append({
            "title": title,
            "score": score,
            "members": members,
            "volumes": volumes,
            "type": type_,
            "_future": future
        })
        
    time.sleep(0.3)
    
print("\nSincronizando resultados (STATUS)...")

for item in data:
    f = item.pop("_future")
    details = f.result()
    item.update(details)


#dataframe bruto
df_before = pd.DataFrame(data)

#limpeza / transformacao(ETL)
#substituir "?" por NaN para analise
df_before["volumes_num"] = pd.to_numeric(df_before["volumes"], errors="coerce")

#remover duplicatas
df_after = df_before.drop_duplicates(subset=["title"])

#remover nulos criticos
df_after = df_after.dropna(subset=["score", "members"])

# remover volumes invalidos para analise
df_after_clean = df_after.dropna(subset=["volumes_num"])


print("\nFinalizado!")
print("Total bruto:", len(df_before))
print("Após limpeza:", len(df_after_clean))

#salvar csv
df_after.to_csv("manga_dataset.csv", index=False)

#grafico antes X depois

plt.figure()
plt.hist(df_before["volumes_num"].dropna(), bins=30)
plt.title("Volumes - ANTES da Limpeza")
plt.show()

plt.figure()
plt.hist(df_after_clean["volumes_num"], bins=30)
plt.title("Volumes - DEPOIS da Limpeza")
plt.show()