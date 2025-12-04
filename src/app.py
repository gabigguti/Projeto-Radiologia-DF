import streamlit as st

st.set_page_config(layout="wide")
st.logo("assets/radiologia-df-logo.png",size="large", icon_image="assets/logo-icon.png")

pages = [
    st.Page("app_pages/dashboard.py", title="Dashboard"),
    st.Page("app_pages/mapa_equipamentos.py", title="Mapa de Equipamentos"),
    st.Page("app_pages/fontes_de_dados.py", title="Dados Brutos"),
    st.Page("app_pages/implementacoes_futuras.py", title="Implementações Futuras"),
    st.Page("app_pages/equipe.py", title="Equipe do Projeto")
]

pg = st.navigation(pages, position="sidebar", expanded=True)

st.markdown(
    """
    <style>
        [data-testid="stSidebar"]::after {
            content: "© 2025 - Projeto Radiologia DF";
            position: absolute;
            bottom: 10px;
            left: 60px;
            font-size: 13px;
            color: #A9A9A9;
        }
    </style>
    """,
    unsafe_allow_html=True
)

pg.run()
