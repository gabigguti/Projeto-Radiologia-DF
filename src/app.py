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

@st.dialog("👋 Bem-vindo(a) ao Projeto Radiologia DF")
def welcome_dialog():
    st.markdown(
        """
        ### Resumo

        Este Painel refere-se ao Projeto Integrador 1 do Centro Universitário de Brasília (CEUB), e apresenta o desenvolvimento de uma solução voltada ao mapeamento e análise dos equipamentos de imagem e temas correlatos no Distrito Federal.
        
        ### Navegação do Menu Lateral

        - **Dashboard**: Gráficos e análises sobre os dados reunidos durante o projeto.  

        - **Mapa de Equipamentos**: Mapa interativo dos equipamentos de imagem do SUS no Distrito Federal.  

        - **Dados Brutos**: Fontes de dados e datasets utilizados para a geração dos gráficos e análises.  

        - **Implementações Futuras**: Melhorias planejadas para o projeto, abrangendo automações, integrações de dados, novos recursos analíticos e aprimoramentos estruturais.  

        - **Equipe do Projeto**: Membros participantes e link para o repositório do projeto. 

        Explore os menus para entender mais sobre a situação de saúde pública do Distrito Federal!
        """
    )

    if st.button("Começar"):
        st.session_state.welcome_shown = True
        st.rerun()   # ⬅️ ESSENCIAL

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False

if not st.session_state.welcome_shown:
    welcome_dialog()

pg.run()
