import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

DATASET_PATH = "dirty_data_pop_df_com_plano_saude_por_ra.csv"

ANO_REFERENCIA = 2021

COL_RA = "Local"
COL_TOTAL = "Total"
COL_COM_PLANO = "Sim"
COL_SEM_PLANO = "Nao"


def limpar_nome_ra(nome: str) -> str:
    if not isinstance(nome, str):
        return None
    n = nome.strip()
    if not n:
        return None
    return n.title()


def tratar_dataset_populacao(caminho: str) -> pd.DataFrame:
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    df = pd.read_csv(caminho, sep=";", engine="python")

    print("Colunas encontradas no CSV:")
    print(df.columns)

    for col in [COL_RA, COL_TOTAL, COL_COM_PLANO, COL_SEM_PLANO]:
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' nao encontrada no CSV. Ajuste as constantes COL_* no script.")

    df_out = pd.DataFrame()
    df_out["nome_ra"] = df[COL_RA].astype(str).apply(limpar_nome_ra)

    df_out["populacao_total"] = (
        pd.to_numeric(df[COL_TOTAL], errors="coerce")
        .fillna(0)
        .astype(int)
        .clip(lower=0)
    )

    df_out["populacao_com_plano_saude"] = (
        pd.to_numeric(df[COL_COM_PLANO], errors="coerce")
        .fillna(0)
        .astype(int)
        .clip(lower=0)
    )

    df_out["populacao_sem_plano_saude"] = (
        pd.to_numeric(df[COL_SEM_PLANO], errors="coerce")
        .fillna(0)
        .astype(int)
        .clip(lower=0)
    )

    df_out["ano"] = ANO_REFERENCIA
    df_out = df_out[df_out["nome_ra"].notna()]

    return df_out


def mapear_id_ra(conn, df: pd.DataFrame) -> pd.DataFrame:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id_ra, nome FROM regiao_administrativa;")
    rows = cur.fetchall()
    cur.close()

    mapa_ra = {r["nome"].strip().lower(): r["id_ra"] for r in rows}

    df["id_ra"] = df["nome_ra"].str.lower().map(mapa_ra)

    faltantes = df[df["id_ra"].isna()]["nome_ra"].unique()
    if len(faltantes) > 0:
        print("\nRAs nao encontradas no banco:")
        for ra in faltantes:
            print("  -", ra)

    return df.dropna(subset=["id_ra"]).copy()


def inserir_populacao(conn, df: pd.DataFrame):
    valores = [
        (
            int(row["id_ra"]),
            int(row["ano"]),
            int(row["populacao_total"]),
            int(row["populacao_com_plano_saude"]),
            int(row["populacao_sem_plano_saude"]),
        )
        for _, row in df.iterrows()
    ]

    if not valores:
        print("Nenhuma linha para inserir.")
        return

    cur = conn.cursor()
    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO populacao
        (id_ra, ano, populacao_total, populacao_plano_saude, populacao_sem_plano_saude)
        VALUES %s;
        """,
        valores,
    )
    conn.commit()
    cur.close()

    print(f"Foram inseridas {len(valores)} linhas na tabela populacao.")


def main():
    print("Tratando dataset de populacao por RA...")
    df = tratar_dataset_populacao(DATASET_PATH)
    print(f"Linhas apos tratamento: {len(df)}")

    conn = get_conn()
    try:
        print("Mapeando id_ra...")
        df_mapeado = mapear_id_ra(conn, df)
        print(f"Linhas apos mapeamento: {len(df_mapeado)}")

        inserir_populacao(conn, df_mapeado)
        print("ETL de populacao concluido.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
