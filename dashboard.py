import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CARREGAR DADOS
# -------------------------

df = pd.read_csv("manga_dataset.csv")

# -------------------------
# SIDEBAR — FILTROS
# -------------------------

st.sidebar.title("Filtros")

tipos = st.sidebar.multiselect(
    "Tipo de publicação",
    df["type"].dropna().unique(),
    default=df["type"].dropna().unique()
)

status_opts = st.sidebar.multiselect(
    "Status de publicação",
    df["status"].dropna().unique(),
    default=df["status"].dropna().unique()
)

# Aplicar filtros
df = df[
    (df["type"].isin(tipos)) &
    (df["status"].isin(status_opts))
]

# -------------------------
# TÍTULO
# -------------------------

st.title("Dashboard de Análise de Mangás — MyAnimeList")
st.write(f"Total de registros exibidos: **{len(df)}**")

# -------------------------
# MÉTRICAS DE CABEÇALHO
# -------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Score Médio",
    round(df["score"].mean(), 2) if not df["score"].isna().all() else "—"
)

col2.metric(
    "Membros Médios",
    f"{int(df['members'].mean()):,}" if not df["members"].isna().all() else "—"
)

col3.metric(
    "Total de Obras",
    len(df)
)

st.divider()

# -------------------------
# GRÁFICO 1 — Boxplot de Score por Status
# Responde à P1: Mangás em publicação têm score maior que finalizados?
# -------------------------

st.subheader("Gráfico 1 — Distribuição de Score por Status de Publicação")
st.caption("Responde à P1: Mangás em publicação possuem score médio maior que mangás finalizados?")

fig1 = px.box(
    df,
    x="status",
    y="score",
    color="status",
    title="Boxplot de Score por Status — Comparação de medianas e dispersão entre grupos",
    labels={"status": "Status de Publicação", "score": "Score Médio"},
)
fig1.update_layout(showlegend=False)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# GRÁFICO 2 — Dispersão Popularidade x Score
# Responde parcialmente à P4
# -------------------------

st.subheader("Gráfico 2 — Popularidade × Score (Membros vs. Nota)")
st.caption("Contribui para a P4: É possível prever popularidade com base no score e volumes?")

fig2 = px.scatter(
    df,
    x="members",
    y="score",
    color="status",
    hover_name="title",
    title="Dispersão: Popularidade × Score — Cada ponto representa uma obra (hover para ver o título)",
    labels={"members": "Número de Membros (popularidade)", "score": "Score"},
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# GRÁFICO 3 — Pizza: Distribuição por Tipo
# Responde à P2: Qual o tipo de mangá mais popular?
# -------------------------

st.subheader("Gráfico 3 — Distribuição de Obras por Tipo de Publicação")
st.caption("Responde à P2: Qual o tipo de mangá mais popular?")

fig3 = px.pie(
    df,
    names="type",
    title="Composição do Ranking por Tipo — Fatia de mercado de cada formato no Top Manga",
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# GRÁFICO 4 — Top 20 mais populares (barras horizontais)
# Contexto geral — obras dominantes
# -------------------------

st.subheader("Gráfico 4 — Top 20 Obras Mais Populares")
st.caption("Contexto geral: quais obras concentram o maior engajamento de membros.")

top20 = df.sort_values("members", ascending=False).head(20)

fig4 = px.bar(
    top20,
    x="members",
    y="title",
    orientation="h",
    title="Top 20 Mangás por Número de Membros — Engajamento acumulado na plataforma",
    labels={"members": "Número de Membros", "title": "Título"},
)

fig4.update_layout(
    margin=dict(l=300, r=30, t=50, b=50),
    height=600,
    yaxis={"categoryorder": "total ascending"},
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------
# GRÁFICO 5 — Histograma de Volumes
# Responde à P3: Quantos volumes em média mangás finalizados têm?
# -------------------------

st.subheader("Gráfico 5 — Distribuição do Número de Volumes por Obra")
st.caption("Responde à P3: Quantos volumes em média mangás finalizados têm?")

# Remover NaN em volumes_num antes de plotar para evitar distorção
df_vol = df.dropna(subset=["volumes_num"])

st.write(f"*Obras com volume informado: {len(df_vol)} de {len(df)} no filtro atual.*")

fig5 = px.histogram(
    df_vol,
    x="volumes_num",
    nbins=30,
    title="Histograma de Volumes — Frequência de obras por faixa de número de volumes publicados",
    labels={"volumes_num": "Número de Volumes", "count": "Quantidade de Obras"},
)

st.plotly_chart(fig5, use_container_width=True)
