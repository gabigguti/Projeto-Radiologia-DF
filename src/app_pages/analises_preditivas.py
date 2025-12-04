import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Análises Preditivas")

# -------------------------
# RESUMO / DESCRIÇÃO
# -------------------------

with st.container():
    st.subheader("🎯 Objetivo das Análises Preditivas")
    st.write("""
    As análises preditivas têm como objetivo **antecipar gargalos** na rede de diagnóstico por imagem
    e **apoiar decisões estratégicas** sobre investimentos, reposição de equipamentos e planejamento operacional.
    """)

    st.subheader("💡 Por que isso é importante?")
    st.write("""
    Essas previsões permitem que gestores:
    - **Justifiquem investimentos** com base em dados;
    - **Planejem a expansão e reposição da frota de mamógrafos**;
    - **Prevejam a demanda de exames até 2027**;
    - **Evitem gargalos antes que eles aconteçam**.
    """)

st.divider()

# -------------------------
# LAYOUT DOS GRÁFICOS / ANÁLISES
# -------------------------

st.subheader("📊 Modelos e Simulações Preditivas")

col1, col2 = st.columns(2)

# --- SIMULAÇÃO 1 ---
with col1:
    with st.container(border=True, height=300):
        st.markdown("### 🔮 Simulação de Impacto de Investimentos")
        st.write("""
        *“Se adicionarmos +10 mamógrafos, o tempo médio de espera cairá X%.”*
        
        Aqui entra o gráfico/simulação do efeito marginal de novos equipamentos,
        podendo ser um line chart, área ou modelo de capacidade.
        """)

# --- SIMULAÇÃO 2 ---
with col2:
    with st.container(border=True, height=300):
        st.markdown("### 📉 Estimativa de Depreciação da Frota")
        st.write("""
        Previsão do desgaste, idade média da frota e necessidade de reposição.
        
        Ideal para usar regressões simples ou curvas de deterioração.
        """)

# ------------------------------------------
# Carregando os dados
# ------------------------------------------
with st.container(border=True, height=1150):
st.markdown("### 🔮 Previsão da demanda de Exames de mamografia")

df_passado = pd.read_csv("data_sets/Demandas_Passadas_Exames_Mamografia.csv")
df_teste = pd.read_csv("data_sets/Demandas_Futuras_Exames_Mamografia_Teste.csv")
df_prev = pd.read_csv("data_sets/Demandas_Futuras_Exames_Mamografia_Previsao.csv")


# Transformar em datas
df_passado["DATE"] = pd.to_datetime(df_passado["DATE"])
df_teste["DATE"] = pd.to_datetime(df_teste["DATE"])
df_prev["DATE"] = pd.to_datetime(df_prev["DATE"])

# ------------------------------------------
# Gráfico (Plotly — mais bonito)
# ------------------------------------------

fig = px.line()

fig.add_scatter(
    x=df_passado["DATE"],
    y=df_passado["Exames"],
    name="Demandas Passadas"
)

fig.add_scatter(
    x=df_teste["DATE"],
    y=df_teste["Exames"],
    name="Demanda Real (Teste)"
)

fig.add_scatter(
    x=df_prev["DATE"],
    y=df_prev["Previsao"],
    name="Previsão SARIMAX"
)

fig.update_layout(
    width=900,
    height=550,
    title="Previsão de Demanda de Exames de Mamografia até o ano de 2027",
)

st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------
    # Mostrar tabelas lado a lado
    # ------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📘 Passado")
        st.dataframe(df_passado, use_container_width=True)

    with col2:
        st.subheader("📙 Teste")
        st.dataframe(df_teste, use_container_width=True)

    with col3:
        st.subheader("📗 Previsão")
        st.dataframe(df_prev, use_container_width=True)
