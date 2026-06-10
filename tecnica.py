import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    ConfusionMatrixDisplay,
)
import matplotlib.pyplot as plt

# -------------------------
# CARREGAR DADOS
# -------------------------

df = pd.read_csv("manga_dataset.csv")

# Remover registros com volumes ausentes (necessário para usar volumes_num como feature)
df = df.dropna(subset=["volumes_num"])

# Informar quantos registros foram efetivamente usados no modelo
print(f"Registros usados no modelo (após remoção de volumes ausentes): {len(df)}")

# -------------------------
# ENGENHARIA DE VARIÁVEIS
# -------------------------

# Variável alvo binária: 1 = popular (acima da mediana de membros), 0 = não popular
df["popular"] = (
    df["members"] > df["members"].median()
).astype(int)

print(f"\nDistribuição da variável alvo 'popular':")
print(df["popular"].value_counts().to_string())

# Features utilizadas
X = df[["score", "volumes_num"]]
y = df["popular"]

# -------------------------
# DIVISÃO TREINO / TESTE (80/20)
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print(f"\nTamanho do conjunto de treino : {len(X_train)} registros")
print(f"Tamanho do conjunto de teste  : {len(X_test)} registros")

# -------------------------
# TREINAMENTO DO MODELO
# -------------------------

modelo = RandomForestClassifier(random_state=42)
modelo.fit(X_train, y_train)

# -------------------------
# PREDIÇÃO
# -------------------------

pred        = modelo.predict(X_test)
pred_proba  = modelo.predict_proba(X_test)[:, 1]  # probabilidades para AUC-ROC

# -------------------------
# MÉTRICAS DE AVALIAÇÃO
# -------------------------

acc = accuracy_score(y_test, pred)
auc = roc_auc_score(y_test, pred_proba)
cm  = confusion_matrix(y_test, pred)

# Extrair valores da matriz de confusão
tn, fp, fn, tp = cm.ravel()

print("\n" + "="*50)
print("RESULTADOS DO MODELO")
print("="*50)

print(f"\nAcurácia             : {acc:.2%}")
print(f"AUC-ROC              : {auc:.4f}")

print("\nRelatório de Classificação (Precisão, Recall, F1-Score):")
print(classification_report(y_test, pred, target_names=["Não Popular", "Popular"]))

print("Matriz de Confusão:")
print(cm)
print(f"  Verdadeiros Negativos (VN): {tn}")
print(f"  Falsos Positivos      (FP): {fp}")
print(f"  Falsos Negativos      (FN): {fn}")
print(f"  Verdadeiros Positivos (VP): {tp}")

# -------------------------
# VISUALIZAÇÃO DA MATRIZ DE CONFUSÃO
# -------------------------

fig, ax = plt.subplots(figsize=(5, 4))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Não Popular", "Popular"])
disp.plot(ax=ax, colorbar=False, cmap="Blues")
ax.set_title("Matriz de Confusão — Random Forest Classifier")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.show()
print("\nMatriz de confusão salva como 'confusion_matrix.png'")

# -------------------------
# RESPOSTA À PERGUNTA ANALÍTICA (P4)
# -------------------------

print("\n" + "="*50)
print("PERGUNTA P4:")
print("É possível prever se um mangá será popular")
print("usando score e quantidade de volumes?")
print("="*50)

if acc >= 0.80:
    print(f"\nResposta: Sim.")
    print(f"O modelo obteve acurácia de {acc:.2%} e AUC-ROC de {auc:.4f},")
    print("demonstrando alta capacidade preditiva com as features selecionadas.")
elif acc >= 0.60:
    print(f"\nResposta: Parcialmente.")
    print(f"O modelo obteve acurácia de {acc:.2%}, encontrando padrões úteis,")
    print("mas com capacidade preditiva moderada.")
else:
    print(f"\nResposta: Não.")
    print(f"O modelo obteve acurácia de {acc:.2%},")
    print("indicando que as features escolhidas têm baixo poder preditivo.")
