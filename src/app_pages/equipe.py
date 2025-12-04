import streamlit as st

st.set_page_config(page_title="Equipe do Projeto", layout="wide")

st.title("Equipe do Projeto")
st.write("Conheça os membros da equipe responsável pelo desenvolvimento deste projeto:")

equipe = [
    {
        "nome": "Thales Rassi",
        "cargo": "Desenvolvimento / Pesquisa",
        "github": "https://github.com/thalesrassi",
        "foto": "https://avatars.githubusercontent.com/u/150684329?v=4",
    },
    {
        "nome": "Gabriel Marques",
        "cargo": "Desenvolvimento / Pesquisa",
        "github": "https://github.com/marquezzin",
        "foto": "https://avatars.githubusercontent.com/u/98905252?v=4",
    },
    {
        "nome": "Gabi Gutierres",
        "cargo": "Pesquisa / UX",
        "github": "https://github.com/gabigguti",
        "foto": "https://avatars.githubusercontent.com/u/119536472?v=4",
    },
    {
        "nome": "Pedro Klein",
        "cargo": "Pesquisa",
        "github": "https://github.com/",
        "foto": "https://avatars.githubusercontent.com/u/104402993?v=4",
    },
    {
        "nome": "Matheus Morais",
        "cargo": "Desenvolvimento / Pesquisa",
        "github": "https://github.com/matheusjosems",
        "foto": "https://avatars.githubusercontent.com/u/141030970?v=4",
    },
    {
        "nome": "Henrique Portal",
        "cargo": "Pesquisa",
        "github": "https://github.com/portalLessa",
        "foto": "https://avatars.githubusercontent.com/u/104402993?v=4",
    },
]

numero_colunas = 6

for i in range(0, len(equipe), numero_colunas):
    cols = st.columns(numero_colunas)
    for col, membro in zip(cols, equipe[i : i + numero_colunas]):
        with col:
            with st.container(border=True):
                # Foto
                st.markdown(
                    f"""
                    <div style="text-align:center;">
                        <img src="{membro['foto']}" 
                             style="width:120px; height:120px; border-radius:50%; margin-top:10px;" />
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                #nome e ícone github
                st.markdown(
                    f"""
                    <div style="text-align:center; margin-top:10px; margin-bottom:4px;">
                        <span style="font-size:1.35rem; font-weight:600;">
                            {membro['nome']}
                        </span>
                        <a href="{membro['github']}" target="_blank" style="margin-left:8px;">
                            <svg height="20" width="20" viewBox="0 0 16 16" 
                                style="fill:white; position:relative; top:-2px; cursor:pointer;">
                                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 
                                    6.53 5.47 7.59.4.07.55-.17.55-.38
                                    0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94
                                    -.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52
                                    -.01-.53.63-.01 1.08.58 1.23.82.72 1.21 
                                    1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78
                                    -.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15
                                    -.08-.2-.36-1.02.08-2.12 0 0 .67-.21 
                                    2.2.82.64-.18 1.32-.27 2-.27.68 0 
                                    1.36.09 2 .27 1.53-1.04 2.2-.82 
                                    2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 
                                    1.27.82 2.15 0 3.07-1.87 3.75-3.65 
                                    3.95.29.25.54.73.54 1.48 0 1.07-.01 
                                    1.93-.01 2.19 0 .21.15.46.55.38A8.013 
                                    8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                            </svg>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Cargo
                st.markdown(
                    f"""
                    <p style="text-align:center; font-size:1rem; color:#cccccc; margin-top:0;">
                        {membro['cargo']}
                    </p>
                    """,
                    unsafe_allow_html=True
                )

                
                