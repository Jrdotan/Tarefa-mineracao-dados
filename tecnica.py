import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

df = pd.read_csv("manga_dataset.csv")

df = df.dropna(subset=["volumes_num"])

df["popular"] = (
    df["members"] > df["members"].median()
).astype(int)

X = df[["score", "volumes_num"]]
y = df["popular"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

modelo = RandomForestClassifier(random_state=42)

modelo.fit(X_train, y_train)

pred = modelo.predict(X_test)

acc = accuracy_score(y_test, pred)

print(f"\nPrecisao do modelo: {acc:.2%}")

print("\nMatriz de Confusão:")
print(confusion_matrix(y_test, pred))

print("\nPergunta:")
print("É possível prever se um mangá será popular usando score e quantidade de volumes?")

if acc >= 0.80:
    print("\nResposta:")
    print("Sim. O modelo apresentou que é bem possível.")
elif acc >= 0.60:
    print("\nResposta:")
    print("Parcialmente. O modelo encontrou padrões úteis, mas a previsão ainda é meio vaga.")
else:
    print("\nResposta:")
    print("Não. Dados apresentaram baixa competencia pra isso.")
