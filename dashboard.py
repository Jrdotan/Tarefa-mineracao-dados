import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CARREGAR DADOS
# -------------------------

df = pd.read_csv("manga_dataset.csv")

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("Filtros")

tipos = st.sidebar.multiselect(
    "Tipo",
    df["type"].dropna().unique(),
    default=df["type"].dropna().unique()
)

status = st.sidebar.multiselect(
    "Status",
    df["status"].dropna().unique(),
    default=df["status"].dropna().unique()
)

# filtro

df = df[
    (df["type"].isin(tipos))
    &
    (df["status"].isin(status))
]

# -------------------------
# TÍTULO
# -------------------------

st.title("Dashboard de Mangás")

st.write(f"Total de registros: {len(df)}")

# -------------------------
# MÉTRICAS
# -------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Score Médio",
    round(df["score"].mean(), 2)
)

col2.metric(
    "Membros Médios",
    f"{int(df['members'].mean()):,}"
)

col3.metric(
    "Mangás",
    len(df)
)

# -------------------------
# GRÁFICO 1
# Score por status
# -------------------------

fig1 = px.box(
    df,
    x="status",
    y="score",
    title="Distribuição de Score por Status"
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# GRÁFICO 2
# Members x Score
# -------------------------

fig2 = px.scatter(
    df,
    x="members",
    y="score",
    color="status",
    hover_name="title",
    title="Popularidade x Score"
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# GRÁFICO 3
# Tipos
# -------------------------

fig3 = px.pie(
    df,
    names="type",
    title="Distribuição por Tipo"
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# GRÁFICO 4
# Top 20 populares
# -------------------------

top20 = df.sort_values(
    "members",
    ascending=False
).head(20)

fig4 = px.bar(
    top20,
    x="members",
    y="title",
    orientation="h",
    title="Top 20 Mangás Mais Populares"
)

fig4.update_layout(
    margin=dict(l=300, r=30, t=50, b=50),
    height=600 # Dá altura suficiente para os 20 itens respirarem
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------
# GRÁFICO 5
# Volumes
# -------------------------

fig5 = px.histogram(
    df,
    x="volumes_num",
    nbins=30,
    title="Distribuição de Volumes"
)

st.plotly_chart(fig5, use_container_width=True)
