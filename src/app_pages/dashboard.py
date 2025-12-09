import streamlit as st
import pandas as pd
import plotly.express as px

from funcoes import (
    gerar_grafico_proporcao_funcionamento,
    gerar_dataset_escassez_SUS,
    kpi_exame_mais_requisitado,
    gerar_grafico_previsao_mamografias,
    kpi_ra_mais_vulneravel,
    kpi_mes_com_mais_mamografias,
    kpi_links_sem_https,
    paginas_com_mais_erros,
    distribuição_wave_bp,
    distribuicao_wave_aria_bp,
    grafico_barras_tempo_espera_df_vs_uf,
    grafico_tendencia_profissionais_radiologia,
)

st.set_page_config(layout="wide")

st.header("Métricas Gerais:")

with st.container():
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    with col1:
        with st.container(border=True):
            kpi_exame_mais_requisitado(pd.read_csv("data_sets/historico_subgrupos_exames_img_mais_requisitados.csv"))

    with col2:
        with st.container(border=True):
            kpi_ra_mais_vulneravel(
                pd.read_csv("data_sets/distribuição_geo_equipamentos.csv"), 
                pd.read_csv("data_sets/pop_df_com_plano_saude_por_ra.csv")
            )

    with col3:
        with st.container(border=True):
            kpi_mes_com_mais_mamografias(pd.read_csv("data_sets/demanda_historica_Exames_Mamografia.csv"))

    with col4:
        with st.container(border=True):
            kpi_links_sem_https(pd.read_csv("data_sets/Dataset_acessibilidade_usabilidade_tratado.csv"))

st.divider()

st.header("Análises de Eficiência Operacional:")

with st.container():
    col1, col2 = st.columns([3,2])

    with col1:  
        with st.container(border=True):
            gerar_grafico_proporcao_funcionamento(pd.read_csv("data_sets/qtd_equip_img_SUS_por_tipo.csv"))
        with st.container(border=True):            
            gerar_dataset_escassez_SUS(pd.read_csv("data_sets/qtd_equip_img_SUS_por_tipo.csv"))

    with col2:
        with st.container(border=True):
            grafico_barras_tempo_espera_df_vs_uf()

st.divider()

st.header("Análises de Acessibilidade do Portal DataSUS:")

with st.container():
    col1, col2, col3 = st.columns([2,2,1])

    with col1:
        with st.container(border=True):
            paginas_com_mais_erros(pd.read_csv("data_sets/Dataset_acessibilidade_usabilidade_tratado.csv"))

    with col2:
        with st.container(border=True):
            distribuição_wave_bp(pd.read_csv("data_sets/Dataset_acessibilidade_usabilidade_tratado.csv"))

    with col3:
        with st.container(border=True):
            distribuicao_wave_aria_bp(pd.read_csv("data_sets/Dataset_acessibilidade_usabilidade_tratado.csv"))

st.divider()

st.header("Análises de Séries Temporais:")

with st.container():
    with st.container(border=True):
            gerar_grafico_previsao_mamografias(pd.read_csv("data_sets/previsao_1_ano.csv"))
    with st.container(border=True):
        grafico_tendencia_profissionais_radiologia(pd.read_csv("data_sets/historico_anual_numero_auxiliares_e_tecnicos_em_radiologia_SUS - Página1 (2).csv"),pd.read_csv("data_sets/historico_anual_numero_cirurgioes_dentistas_radiologistas_SUS - denstista_radio_profissinoais.csv.csv"), pd.read_csv("data_sets/historico_anual_numero_medicos_radiologistas_e_diagnostico_imagem_SUS - cnes_cnv_proc02df001944189_6_37_247.csv.csv"))

