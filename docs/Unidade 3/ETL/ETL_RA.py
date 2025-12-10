import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

DATASETS_RA = [
    {
        "caminho": "dirty_data_distribuição_geografica_equipamentos_DF.csv",
        "coluna_ra": "ra",     
        "sep": ",",            
        "skiprows": 0, 
        "skipfooter": 0,        
    },
    {
        "caminho": "dirty_data_populacao_DF_com_plano_saude_por_RA.csv",
        "coluna_ra": "Local",
        "sep": ",",
        "skiprows": 1,
        "skipfooter": 2,
    },
]


def extrair_ras_unicas() -> pd.DataFrame:
    lista_series = []

    for cfg in DATASETS_RA:
        caminho = cfg["caminho"]
        coluna_ra = cfg["coluna_ra"]
        sep = cfg.get("sep", ",")
        skiprows = cfg.get("skiprows", 0)
        skipfooter = cfg.get("skipfooter", 0)

        if not os.path.exists(caminho):
            print(f"Aviso: arquivo nao encontrado, pulando: {caminho}")
            continue

        df = pd.read_csv(caminho, sep=sep, skiprows=skiprows, skipfooter=skipfooter, engine="python")
        if coluna_ra not in df.columns:
            print(f"Aviso: coluna {coluna_ra} nao encontrada em {caminho}, colunas: {df.columns}")
            continue

        s_ra = df[coluna_ra].dropna().astype(str)
        lista_series.append(s_ra)

    if not lista_series:
        raise ValueError("Nao foi possivel extrair nenhuma RA. Verifique DATASETS_RA e arquivos.")

    todas_ras = pd.concat(lista_series, ignore_index=True)

    todas_ras = todas_ras.str.strip()
    todas_ras = todas_ras.replace("", pd.NA).dropna()

    todas_ras = todas_ras.str.title()

    df_ras = pd.DataFrame({"nome_ra": todas_ras})
    df_ras = df_ras.drop_duplicates().sort_values("nome_ra").reset_index(drop=True)

    return df_ras



ID_UF_DF = 1 

def carregar_regioes_administrativas(conn, df_ras: pd.DataFrame) -> None:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT nome FROM regiao_administrativa WHERE id_uf = %s;", (ID_UF_DF,))
    existentes = {row["nome"] for row in cur.fetchall()}

    novas_linhas = []
    for _, row in df_ras.iterrows():
        nome_ra = row["nome_ra"].strip()
        if nome_ra not in existentes:
            novas_linhas.append((nome_ra, ID_UF_DF))

    if novas_linhas:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO regiao_administrativa (nome, id_uf)
            VALUES %s
            """,
            novas_linhas,
        )
        conn.commit()
        print(f"Foram inseridas {len(novas_linhas)} novas RAs.")
    else:
        print("Nenhuma nova RA para inserir.")

    cur.close()


def main():
    print("Extraindo RAs unicas a partir dos datasets...")
    df_ras = extrair_ras_unicas()
    print(f"Total de RAs unicas encontradas: {len(df_ras)}")

    conn = get_conn()
    try:
        carregar_regioes_administrativas(conn, df_ras)
        print("ETL de Região Administrativa concluído.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
