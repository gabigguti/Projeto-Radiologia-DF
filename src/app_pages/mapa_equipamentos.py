import streamlit as st
import json
import pandas as pd
import plotly.express as px

st.title("Mapa de equipamentos de imagem por Região Administrativa - DF")

with st.expander("Como usar o mapa?"):
    st.markdown("""
### Guia rápido
- Use o **menu suspenso** acima do mapa para escolher o tipo de equipamento.
- Passe o mouse sobre uma Região Administrativa para ver os valores.
- O mapa pode ser **arrastado, ampliado e reduzido** normalmente.
- Clique no ícone do Plotly para salvar ou visualizar em tela cheia.
    """)

st.divider()

GEOJSON_PATH = "data_sets/Limite_RA_20190.json"    # arquivo das RAs do DF
RA_FIELD_GJ   = "ra"    # campo de nome da RA no GeoJSON
CSV_PATH      = "data_sets/distribuição_geo_equipamentos.csv"

df = pd.read_csv(CSV_PATH)

# cópia do df pra trabalhar
base = df.copy()

# seleção das métricas, no caso equipamentos
metricas_equip = [
    c for c in base.columns
    if c != "ra" and pd.api.types.is_numeric_dtype(base[c])
]
if not metricas_equip:
    raise ValueError("Não encontrei colunas numéricas além de 'ra'. Verifique seu DataFrame.")

# label bonitinho pras colunas
metric_labels = {
    "qtd_gama_camara": "Gama Câmara",
    "qtd_mamografo_comando_simples": "Mamógrafo Comando Simples",
    "qtd_mamografo_estereotaxia": "Mamógrafo Estereotaxia",
    "qtd_raio_X_100_mA": "Raio X até 100 mA",
    "qtd_raio_X_100_500_mA": "Raio X de 100 a 500 mA",
    "qtd_raio_X_mais_500_mA": "Raio X mais de 500mA",
    "qtd_raio_X_dentario": "Raio X Dentário",
    "qtd_raio_X_fluoroscopia": "Raio X com Fluoroscopia",
    "qtd_raio_X_densitometria_ossea": "Raio X para Densitometria Ossea",
    "qtd_raio_X_hemodinamica": "Raio X para Hemodinâmica",
    "qtd_ressonancia_magnetica": "Ressonância Magnética",
    "qtd_tomógrafo_computadorizado": "Tomógrafo Computadorizado",
    "qtd_ultrassom_doppler_colorido": "Ultrassom Doppler Colorido",
    "qtd_ultrassom_ecografo": "Ultrassom Ecografo",
    "qtd_ultrassom_convencional": "Ultrassom Convencional",
    "qtd_processadora_de_filme_mamografia": "Processadora de Filme Exclusiva Mamografia",
    "qtd_mamografo_computadorizado": "Mamógrafo Computadorizado",
    "qtd_pet_ct": "PET/CT"
}

# Se existir alguma métrica sem label definido, usa o próprio nome da coluna
def get_label(col):
    return metric_labels.get(col, col)

# carregamento do geoJSON
with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    gj = json.load(f)

# criação de um dicionário com label como chave e coluna como valor
opcoes_dict = {get_label(col): col for col in metricas_equip}

# selectbox mostra os labels bonitinhos
label_selecionado = st.selectbox(
    "Selecione o tipo de equipamento:",
    options=list(opcoes_dict.keys()),
    index=0
)

# recuperação da coluna correspondente
metrica_selecionada = opcoes_dict[label_selecionado]

# criação do mapa
fig = px.choropleth_mapbox(
    base,
    geojson=gj,
    locations="ra",
    featureidkey=f"properties.{RA_FIELD_GJ}",
    color=metrica_selecionada,
    color_continuous_scale="Viridis",
    mapbox_style="open-street-map",
    opacity=0.62
)

# Centralização no DF
fig.update_layout(
    mapbox_zoom=9,
    mapbox_center={"lat": -15.80, "lon": -47.90},
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title=label_selecionado),
    height=800,
    font=dict(size=16, color="black")
)

# Hover com o equipamento selecionado
fig.data[0].hovertemplate = (
    f"<b>%{{properties.{RA_FIELD_GJ}}}</b><br>"
    f"Total de equipamentos {label_selecionado}: %{{z}}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})