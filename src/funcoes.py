import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

#funções que geram kpi
def kpi_exame_mais_requisitado(df):
    # renomeia colunas para nomes mais curtos pra caber na kpi
    df = df.rename(columns={
        "Diagnostico por radiologia": "Radiologia",
        "Diagnostico por ultrasonografia": "Ultrasonografia",
        "Diagnostico por tomografia": "Tomografia",
        "Diagnostico por ressonancia magnetica": "Ressonancia magnetica",
        "Diagnostico por endoscopia": "Endoscopia",
        "Diagnostico por radiologia intervencionista": "Radiologia intervencionista"
    })

    # Identifica colunas de subgrupos (tira ano e total)
    colunas_subgrupo = [c for c in df.columns if c not in ["Ano atendimento", "Total"]]

    # Ano mais recente e ano anterior
    ano_recente = df["Ano atendimento"].max()
    ano_anterior = ano_recente - 1

    # Linha do ano mais recente
    linha_recente = df.loc[df["Ano atendimento"] == ano_recente, colunas_subgrupo].iloc[0]

    # Subgrupo com maior número de exames no ano mais recente
    subgrupo_topo = linha_recente.idxmax()
    valor_recente = linha_recente.max()

    # Linha do ano anterior (se existir)
    linha_anterior = df.loc[df["Ano atendimento"] == ano_anterior, colunas_subgrupo]

    if not linha_anterior.empty:
        valor_anterior = linha_anterior[subgrupo_topo].iloc[0]
        diferenca_absoluta = valor_recente - valor_anterior
        if valor_anterior != 0:
            diferenca_percentual = (diferenca_absoluta / valor_anterior) * 100
        else:
            diferenca_percentual = None
    else:
        valor_anterior = None
        diferenca_absoluta = None
        diferenca_percentual = None

    # Texto da variação (delta)
    if diferenca_absoluta is None or diferenca_percentual is None:
        texto_delta = "Sem dado do ano anterior"
    else:
        texto_delta = f"{diferenca_percentual:+.1f}% em relação ao ano de {ano_anterior}".replace(",", ".")

    # Métrica no topo do dashboard
    st.metric(
        label=f"Grupo de exames de imagem mais realizado no SUS em {ano_recente}",
        value=f"{subgrupo_topo}",
        delta=texto_delta,
        help=("Esta métrica refere-se ao grupo de exames de imagem mais requisitado," 
        "ou seja, aquele com o maior número de registros de realizações encontrados "
        "nas bases de dados do Ministério da Saúde no ano vigente \n\n"
        "Última Atualização em 03/12/2025"),
        delta_color="normal" 
    )

def kpi_ra_mais_vulneravel(df1,df2):
    equip = df1
    pop = df2

    #padronização nomes das RAs
    equip["ra"] = equip["ra"].str.strip().str.lower()

    #renomeação coluna local pra ra
    pop = pop.rename(columns={"Local": "ra"})
    pop["ra"] = pop["ra"].str.strip().str.lower()

    # remoção linha agregada do DF, se existir
    pop = pop[pop["ra"] != "df"]

    # Soma do total de equipamentos por RA
    equip_cols = [c for c in equip.columns if c != "ra"]
    equip["total_equipamentos"] = equip[equip_cols].sum(axis=1)

    # Calculo da proporção de pessoas sem plano
    pop["prop_sem_plano"] = pop["Nao"] / pop["Total"]

    # Junção das duas bases
    df = equip.merge(pop[["ra", "prop_sem_plano"]], on="ra", how="left")

    # Ranking: menos equipamentos = pior (rank crescente)
    df["rank_equip"] = df["total_equipamentos"].rank(method="min")

    # Ranking: maior proporção sem plano = pior (rank decrescente)
    df["rank_pobreza_plano"] = df["prop_sem_plano"].rank(ascending=False, method="min")

    # Score combinado: quanto menor, mais vulnerável
    df["score"] = df["rank_equip"] + df["rank_pobreza_plano"]

    ra_pior = df.loc[df["score"].idxmin()]

    ra_nome = ra_pior["ra"].title()
    total_equip = int(ra_pior["total_equipamentos"])
    prop_sem_plano = ra_pior["prop_sem_plano"] * 100

    st.metric(
        label="Região Administrativa com situação de saúde mais vulnerável",
        value=f"{ra_nome}",
        delta=f"{prop_sem_plano:.1f}% sem plano de saúde",
        help=(
            "Esta métrica refere-se à Região Administrativa mais vulnerável do Distrito Federal, "
            "ou seja, aquela que possui o menor número de equipamentos de imagem em sua área "
            "e o maior percentual de pessoas sem plano de saúde.\n\n"
            "Última atualização: 03/12/2025."
        ),
        delta_color="off"
    )

def kpi_mes_com_mais_mamografias(df):

    MESES_PT = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    df["DATE"] = pd.to_datetime(df["DATE"])

    df["ano"] = df["DATE"].dt.year
    df["mes"] = df["DATE"].dt.month

    ano_atual = df["ano"].max()
    ano_anterior = ano_atual - 1

    df_atual = df[df["ano"] == ano_atual]

    # Mês com mais mamografias no ano atual
    linha_top_atual = df_atual.loc[df_atual["Exames"].idxmax()]
    mes_top_atual = int(linha_top_atual["mes"])
    mes_nome_atual = MESES_PT[mes_top_atual]
    exames_atual = int(linha_top_atual["Exames"])

    # busca do mês com MAIS exames no ano anterior
    df_anterior = df[df["ano"] == ano_anterior]

    if not df_anterior.empty:
        linha_top_anterior = df_anterior.loc[df_anterior["Exames"].idxmax()]
        mes_top_anterior = int(linha_top_anterior["mes"])
        mes_nome_anterior = MESES_PT[mes_top_anterior]
        exames_anterior = int(linha_top_anterior["Exames"])
        
        diff = exames_atual - exames_anterior
        diff_pct = (diff / exames_anterior) * 100 if exames_anterior > 0 else None

        if diff_pct is not None:
            delta_text = f"{diff_pct:+.1f}% em relação ao mês mais requisitado ({mes_nome_anterior}) de {ano_anterior}"
        else:
            delta_text = f"{diff:+} exames vs. {mes_nome_anterior}/{ano_anterior}"
    else:
        exames_anterior = None
        diff = 0
        delta_text = "Sem dados do ano anterior"
  
    # KPI final
    st.metric(
        label=f"Mês com mais mamografias em {ano_atual}",
        value=f"{mes_nome_atual}",
        delta=delta_text,
        help=(
            "Esta métrica identifica o mês com maior número de mamografias realizadas no ano vigente,"
            " e o compara com o mês de maior volume registrado no ano anterior. \n\n"
            "Última atualização: 03/12/2025."
        ),
        delta_color="normal"
    )

def kpi_links_sem_https(df):
    col = "Links"

    # normalização de valores
    df[col] = df[col].astype(str).str.strip().str.lower()

    # links que começam com HTTPS (válidos)
    mask_https = df[col].str.startswith("https://", na=False)

    total = len(df)
    com_https = mask_https.sum()
    sem_https = total - com_https

    perc_sem_https = (sem_https / total) * 100 if total > 0 else 0
    perc_com_https = (com_https / total) * 100 if total > 0 else 0

    st.metric(
        label="Páginas que NÃO implementam HTTPS",
        value=f"{perc_sem_https:.1f}% sem criptografia",
        help=("Esta métrica representa a porcentagem de páginas do portal DataSUS" 
        " que encontram-se vulneráveis por não adotarem o protocolo HTTPS no ano vigente \n\n"
        "Última Atualização em 03/12/2025"),
        height=100
    )

#funções que geram gráfico
def gerar_grafico_proporcao_funcionamento(df):
    st.subheader("Proporção de Funcionamento dos Equipamentos do SUS no DF:")

    df["parados"] = df["existentes_SUS"] - df["em_uso_SUS"]

    df["pct_em_uso"] = (df["em_uso_SUS"] / df["existentes_SUS"]) * 100
    df["pct_parados"] = (df["parados"] / df["existentes_SUS"]) * 100

    #filtro
    equip_sel = st.selectbox("Selecione o equipamento desejado",  
        df["equipamento"].unique(), 
        width=300, 
        help="Selecione o equipamento para visualizar sua proporção de funcionamento.")

    # Filtragem de equipamento selecionado
    df_sel = df[df["equipamento"] == equip_sel].copy()

    # Transformar para formato longo
    df_melt = df_sel.melt(
        id_vars="equipamento",
        value_vars=["pct_em_uso", "pct_parados"],
        var_name="status",
        value_name="percentual"
    )

    #merge
    df_melt["status"] = df_melt["status"].map({
        "pct_em_uso": "Em funcionamento",
        "pct_parados": "Parado"
    })

    #texto de porcentagem
    df_melt["pct_text"] = "<b>" + df_melt["percentual"].round(1).astype(str) + "%</b>"
    
    fig = px.bar(
        df_melt,
        x="percentual",
        y="equipamento",
        color="status",
        text="pct_text",   
        orientation="h",
        barmode="stack",
        color_discrete_map={
            "Em funcionamento": "#1A9988",   
            "Parado": "#A6313E"     
        }
    )

    fig.update_traces(
        textposition="inside",   
        insidetextanchor="middle", 
        textfont=dict(size=13, color="white")
    )

    fig.update_layout(
        title=f"{equip_sel}",
        xaxis_title="Percentual (%)",
        yaxis_title="",
        bargap=0.25,
        height=210
    )
    fig.update_yaxes(showticklabels=False)

    st.plotly_chart(fig, use_container_width=True)

    st.write("Última atualização em: dd/mm/aaaa")

def gerar_dataset_escassez_SUS(df):
    df["privado"] = df["existentes"] - df["existentes_SUS"]
    df["publico"] = df["existentes_SUS"]

    df["Desigualdade Percentual"] = ((df["privado"] - df["publico"]) / df["publico"]) * 100

    df_rank = df[["equipamento", "privado", "publico", "Desigualdade Percentual"]].copy()

    df_rank = df_rank.sort_values("Desigualdade Percentual", ascending=False)

    st.subheader("Ranking da Desigualdade de Equipamentos na Rede Privada X Pública")

    st.dataframe(
        df_rank,
        use_container_width=True,
        height=300, 
        column_config={
            "Desigualdade Percentual": st.column_config.NumberColumn(
                "Desigualdade Percentual",
                help="Diferença percentual entre rede privada e SUS",
                format="%.2f%%"
            )
        }
    )

    st.write("Última atualização em: dd/mm/aaaa")

def gerar_grafico_previsao_mamografias(df):
    st.subheader("Projeção do Número de Mamografias no DF para 2026 com Modelo Estatístico de Séries Temporais SARIMAX (ARIMA Sazonal com Regressão Exógena)")
    df_prev = df
    df_prev["DATE"] = pd.to_datetime(df_prev["DATE"])

    data_corte = pd.to_datetime("2025-10-01")

    # Separar histórico e futuro
    df_antes = df_prev[df_prev["DATE"] < data_corte]
    df_depois = df_prev[df_prev["DATE"] >= data_corte]

    fig = px.line()

    fig.add_scatter(
        x=df_antes["DATE"],
        y=df_antes["Exames"],
        name="Histórico / Ajustado",
        line=dict(color="#1f77b4", width=2)
    )

    fig.add_scatter(
        x=df_depois["DATE"],
        y=df_depois["Exames"],
        name="Previsão SARIMAX",
        line=dict(color="red", width=2)
    )

    fig.update_layout(
        width=900,
        height=359,
        title="Previsão de Demanda de Exames de Mamografia até 2026",
        xaxis_title="Data",
        yaxis_title="Quantidade de Exames"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write("Última Atualização em 03/12/2025")

def paginas_com_mais_erros(df):
    st.subheader("Ranking das Páginas do Portal DataSUS com Maior Número de Erros de Acessibilidade Segundo o WAVE - Accessibility Evaluation Tool")
    # Limpeza de espaços no nome das colunas
    df.columns = df.columns.str.strip()

    # Remoção de colunas completamente vazias
    colunas_vazias = [c for c in df.columns if df[c].isna().all()]
    df = df.drop(columns=colunas_vazias)

    # Conversão em colunas numéricas (se tiver alguma lida como string)
    for col in df.columns:
        if col not in ["TELA", "Links"] and df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="ignore")

    # Slider para escolher quantas páginas mostrar
    top_n = st.number_input(
        "Quantidade de páginas a serem classificadas",
        min_value=5,
        max_value=min(100, len(df)),
        value=10,
        width=290,
        help="Selecione o número de páginas que deseja classificar de acordo como o número de erros de acessibilidade existentes",
        step=1
    )

    
    df_top = df.nlargest(top_n, "Errors")
    
    fig = px.bar(
        df_top,
        x="TELA",
        y="Errors",
        hover_data=["Links"],
        labels={"TELA": "ID da página (TELA)", "Errors": "Quantidade de erros"},
        title=f"Top {top_n} páginas com mais erros: WAVE - Accessibility Evaluation Tool"
    )
    
    fig.update_layout(
        xaxis_type="category",
        height=524
    )
    
    st.plotly_chart(fig, use_container_width=True)

    st.write("Última atualização em: dd/mm/aaaa")

def distribuição_wave_bp(df):
    st.subheader("Diagrama de Caixa dos Erros e Alertas Identificiados nas Páginas do Portal DataSUS pelo WAVE - Accessibility Evaluation Tool")

    # ----------------------------------------
    # LIMPEZA LEVE
    # ----------------------------------------
    # Remove espaços no nome das colunas (ex.: 'Links ' -> 'Links')
    df.columns = df.columns.str.strip()

    # Remove colunas completamente vazias (ex.: 'Unnamed: 9')
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    df = df.drop(columns=empty_cols)

    # Converte colunas numéricas (se houver alguma lida como string)
    for col in df.columns:
        if col not in ["TELA", "Links"] and df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="ignore")

    # ----------------------------------------
    # IDENTIFICAR MÉTRICAS PRINCIPAIS
    # ----------------------------------------
    numeric_cols = [
        c for c in df.columns
        if c not in ["TELA", "Links"] and pd.api.types.is_numeric_dtype(df[c])
    ]

    # Vou assumir estas colunas principais (presentes no seu dataset):
    # Errors, Contrast Errors, Alerts, Features, Structure, ARIA, AIM Score
    main_metrics = [c for c in numeric_cols if c in [
        "Errors", "Contrast Errors", "Alerts", "AIM Score"
    ]]
    if not main_metrics:
        main_metrics = numeric_cols  # fallback

    # Métricas de contagem (problemas detectados por página)
    count_metrics = ["Errors", "Contrast Errors", "Alerts"]

    # Garante que existem no dataframe
    count_metrics = [m for m in count_metrics if m in df.columns]

    # Deixa os dados em formato "longo" para o boxplot
    df_box_counts = df[count_metrics].melt(
        var_name="Métrica",
        value_name="Valor"
    )

    # Remove linhas com NaN só por segurança
    df_box_counts = df_box_counts.dropna(subset=["Valor"])

    # Boxplot das métricas de erro/alerta
    fig_counts = px.box(
        df_box_counts,
        x="Métrica",
        y="Valor",
        points="outliers",
        title="Distribuição de Errors, Contrast Errors e Alerts: WAVE - Accessibility Evaluation Tool"
    )

    fig_counts.update_layout(height=608)

    st.plotly_chart(fig_counts, use_container_width=True)

    st.write("Última atualização em: dd/mm/aaaa")

def distribuicao_wave_aria_bp(df):
    st.subheader("Diagrama de Caixa dos ARIA'S Identificiados nas Páginas do Portal DataSUS pelo WAVE - Accessibility Evaluation Tool")
    # ----------------------------------------
    # LIMPEZA LEVE
    # ----------------------------------------
    # Remove espaços no nome das colunas (ex.: 'Links ' -> 'Links')
    df.columns = df.columns.str.strip()

    # Remove colunas completamente vazias (ex.: 'Unnamed: 9')
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    df = df.drop(columns=empty_cols)

    # Converte colunas numéricas (se houver alguma lida como string)
    for col in df.columns:
        if col not in ["TELA", "Links"] and df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="ignore")

    # ----------------------------------------
    # IDENTIFICAR MÉTRICAS PRINCIPAIS
    # ----------------------------------------
    numeric_cols = [
        c for c in df.columns
        if c not in ["TELA", "Links"] and pd.api.types.is_numeric_dtype(df[c])
    ]

    # Vou assumir estas colunas principais (presentes no seu dataset):
    # Errors, Contrast Errors, Alerts, Features, Structure, ARIA, AIM Score
    main_metrics = [c for c in numeric_cols if c in [
        "Errors", "Contrast Errors", "Alerts", "AIM Score"
    ]]
    if not main_metrics:
        main_metrics = numeric_cols  # fallback

    # Métricas de contagem (problemas detectados por página)
    count_metrics = ["Errors", "Contrast Errors", "Alerts"]

    # Garante que existem no dataframe
    count_metrics = [m for m in count_metrics if m in df.columns]

    # Deixa os dados em formato "longo" para o boxplot
    df_box_counts = df[count_metrics].melt(
        var_name="Métrica",
        value_name="Valor"
    )

    # Remove linhas com NaN só por segurança
    df_box_counts = df_box_counts.dropna(subset=["Valor"])
    # ----------------------------------------
    # Boxplot separado para o AIM Score
    # ----------------------------------------
    if "AIM Score" in df.columns:
        df_box_score = (
            df[["AIM Score"]]
            .replace(-1, np.nan)             # trata -1 como missing
            .dropna(subset=["AIM Score"])    # remove os faltantes
            .rename(columns={"AIM Score": "AIM_Score"})
        )

        fig_score = px.box(
            df_box_score,
            y="AIM_Score",
            points="outliers",
            title="Distribuição WAVE AIM Score das páginas"
        )
        fig_score.update_layout(height=508)
        st.plotly_chart(fig_score, use_container_width=True)

    st.write("Última atualização em: dd/mm/aaaa")

def carregar_mamografia_uf(uf: str) -> pd.DataFrame:
    caminho = f"data_sets/estados/mamografia_atend{uf.lower()}.csv"
    df = pd.read_csv(caminho, sep=";")
    return df

def preparar_distribuicao_tempo(df: pd.DataFrame) -> pd.DataFrame:
    cols_intervalo = ["0 - 10 dias", "11 - 20 dias", "21 - 30 dias", "> 30 dias"]

    cols_intervalo = [c for c in cols_intervalo if c in df.columns]

    for c in cols_intervalo:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["Ano Resultado"] = pd.to_numeric(df["Ano Resultado"], errors="coerce")
    df = df.dropna(subset=["Ano Resultado"])

    df = df.sort_values("Ano Resultado")
    df_3anos = df.tail(3)

    soma = df_3anos[cols_intervalo].sum()
    total = soma.sum()

    dist = soma.reset_index()
    dist.columns = ["intervalo", "qtd"]
    dist["pct"] = (dist["qtd"] / total) * 100

    return dist

def grafico_barras_tempo_espera_df_vs_uf():
    st.subheader("Comparação DF X Brasil em Tempo de Espera para Realização de Mamografias nos últimos 3 anos")
    ufs_disponiveis = [
        "AC","AL","AM","AP","BA","CE","ES","GO","MA","MG","MS","MT","PA","PB",
        "PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"
    ]

    uf_escolhida = st.selectbox(
        "Selecione a UF para comparação",
        options=ufs_disponiveis,
        help=("Selecione a Unidade da Federação para comparação do tempo de espera (intervalo de tempo entre a solicitação do exame até a realização efetiva) com o Distrito Federal nos últimos 3 anos"),
        width=250,
        index=24  
    )

    # Carrega dados
    df_df = carregar_mamografia_uf("DF")
    df_uf = carregar_mamografia_uf(uf_escolhida)

    # Prepara distribuição percentual
    dist_df = preparar_distribuicao_tempo(df_df)
    dist_uf = preparar_distribuicao_tempo(df_uf)

    dist_df["UF"] = "DF"
    dist_uf["UF"] = uf_escolhida

    df_comp = pd.concat([dist_df, dist_uf], ignore_index=True)

    fig = px.bar(
        df_comp,
        x="intervalo",
        y="pct",
        color="UF",
        color_discrete_sequence=px.colors.qualitative.Dark24,
        barmode="group",
        text="pct",
        labels={
            "intervalo": "Intervalo de tempo de espera",
            "pct": "Percentual de exames (%)",
            "UF": "Unidade da Federação"
        },
        title=f"Tempo de espera para Realização de mamografias DF vs {uf_escolhida}"
    )

    fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="Percentual de exames (%)",
        xaxis_title="Intervalo de tempo de espera",
        legend_title="UF",
        uniformtext_minsize=8,
        height=628,
        uniformtext_mode="hide"
    )
    fig.update_yaxes(range=[0, 100])

    st.plotly_chart(fig, use_container_width=True)

    st.write("Última atualização em: dd/mm/aaaa")

def parse_data_mensal(s: str):

    MES_MAP = {
    "jan.": 1, "fev.": 2, "mar.": 3, "abr.": 4, "mai.": 5, "jun.": 6,
    "jul.": 7, "ago.": 8, "set.": 9, "out.": 10, "nov.": 11, "dez.": 12
    }

    if pd.isna(s):
        return pd.NaT
    try:
        ano, mes = str(s).split("/")
        mes = mes.strip()
        m = MES_MAP.get(mes)
        return pd.Timestamp(int(ano), m, 1)
    except Exception:
        return pd.NaT

def grafico_tendencia_profissionais_radiologia(df1,df2,df3):
    st.subheader("Tendência temporal de profissionais de radiologia por categoria (2007-2025)")
    df_aux = df1
    df_dent = df2
    df_med = df3

    # tratamento de data
    df_aux["data"] = df_aux["Data"].apply(parse_data_mensal)
    df_dent["data"] = df_dent["Ocupações de Nível Superior"].apply(parse_data_mensal)
    df_med["data"] = df_med["Ano/mês compet."].apply(parse_data_mensal)

    # Remoção linhas sem data por segurança
    df_aux = df_aux.dropna(subset=["data"])
    df_dent = df_dent.dropna(subset=["data"])
    df_med = df_med.dropna(subset=["data"])

    #deixando tudo no formato longo
    # 1) Auxiliares e técnicos
    aux_long = df_aux.melt(
        id_vars="data",
        value_vars=[
            "Auxiliar de Radiologia Revelação",
            "Tecnico em Radiologia e Imagenologia"
        ],
        var_name="categoria",
        value_name="quantidade"
    )

    # 2) Dentistas radiologistas
    df_dent = df_dent.rename(
        columns={"Cirurgião dentista - radiologista": "Cirurgião dentista radiologista"}
    )
    dent_long = df_dent[["data", "Cirurgião dentista radiologista"]].melt(
        id_vars="data",
        var_name="categoria",
        value_name="quantidade"
    )

    # 3) Médicos radiologistas
    med_long = df_med[["data", "Radiologistas"]].melt(
        id_vars="data",
        var_name="categoria",
        value_name="quantidade"
    )

    # Junção
    df_long = pd.concat([aux_long, dent_long, med_long], ignore_index=True)

    df_long = df_long.sort_values("data")

    fig = px.line(
        df_long,
        x="data",
        y="quantidade",
        color="categoria",
        markers=True,
        labels={
            "data": "Ano / mês",
            "quantidade": "Número de profissionais",
            "categoria": "Tipo de profissional"
        },
        title="Tendência temporal de profissionais de radiologia por categoria"
    )

    fig.update_layout(
        legend_title="Tipo de profissional",
        hovermode="x unified",
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write("Última Atualização em 03/12/2025")



