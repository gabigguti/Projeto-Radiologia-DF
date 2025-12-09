import streamlit as st
import pandas as pd

st.title("Fontes de Dados")

# Lista das bases de dados
fontes_dados = [
    {
        "nome": "DATASUS – TABNET",
        "logo": "https://datasus.saude.gov.br/wp-content/uploads/2019/12/Tabnet-topo-2.png",
        "link": "https://datasus.saude.gov.br/"
    },
    {
        "nome": "CNES – Cadastro Nacional de Estabelecimentos de Saúde",
        "logo": "https://cnes.datasus.gov.br/img/img_cnes_logo.png",
        "link": "https://cnes2.datasus.gov.br/"
    },
    {
        "nome": "IBGE – Instituto Brasileiro de Geografia e Estatistica",
        "logo": "https://www.ibge.gov.br/templates/novo_portal_base/imagens/logo_mobile.png",
        "link": "https://www.ibge.gov.br/"
    },
    {
        "nome": "IPEDF – Instituto de Pesquisa e Estatística do Distrito Federal",
        "logo": "https://pdad.ipe.df.gov.br/assets/logo-ipedf.svg",
        "link": "https://www.ipe.df.gov.br/"
    },
    {
        "nome": "SISCAN – Sistema de Informação do Câncer",
        "logo": "https://www.gov.br/transferegov/pt-br/noticias/noticias/arquivos-e-imagens/ministerio-da-saude.png",
        "link": "https://datasus.saude.gov.br/acesso-a-informacao/sistema-de-informacao-do-cancer-siscan-colo-do-utero-e-mam"
    },
]

# Quantas colunas por linha você quer
cols_por_linha = 6

for i in range(0, len(fontes_dados), cols_por_linha):
    row = fontes_dados[i:i+cols_por_linha]
    cols = st.columns(len(row))

    for col, fonte in zip(cols, row):
        with col:
            with st.container(border=True, height=300):
                st.image(fonte["logo"], width="stretch")
                st.subheader(f"**{fonte['nome']}**")
                st.link_button(
                    label="Acessar Base",
                    url=fonte["link"]
                )

df_distribuicao = pd.read_csv("data_sets/distribuição_geo_equipamentos.csv")
df_populacao_plano = pd.read_csv("data_sets/pop_df_com_plano_saude_por_ra.csv")
df_demanda_radiologia = pd.read_csv("data_sets/historico_subgrupos_exames_img_mais_requisitados.csv")
df_erros_acessibilidade = pd.read_csv("data_sets/Dataset_acessibilidade_usabilidade_tratado.csv")

st.title("Dados Brutos")
st.write(
    "Confira abaixo uma amostra de alguns dos dados coletados durante o projeto. "
    "Para ver a totalidade dos dados, visite o repositório no GitHub."
)

# 1: Distribuição geográfica dos equipamentos
st.subheader("Distribuição geográfica de equipamentos de imagem")
st.dataframe(
    df_distribuicao,
    width="stretch",
)

# 2: Duas colunas – população com plano x demanda de exames
col1, col2 = st.columns(2)

with col1:
    st.subheader("População do DF com acesso a planos de saúde")
    st.dataframe(
        df_populacao_plano,
        width="stretch",
    )

with col2:
    st.subheader("Demanda de exames de radiologia")
    st.dataframe(
        df_demanda_radiologia,
        width="stretch",
    )

# 3: Erros de acessibilidade no DATASUS
st.subheader("Erros de acessibilidade no DATASUS")
st.dataframe(
    df_erros_acessibilidade,
    width="stretch",
)
