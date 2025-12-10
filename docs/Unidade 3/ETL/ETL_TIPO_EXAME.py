import os
import re
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

DATASET_EXAMES = "dirty_data_historico_grupos_exames_img_mais_requisitados.csv"

COLUNAS_IGNORAR = [
    "Ano atendimento",
    "Total",
]

def limpar_nome_exame(col: str) -> str:
    original = col

    col = col.strip()
    col = col.lower()

    col = re.sub(r"\d+", "", col)

    col = col.replace("_", " ")
    col = col.replace("-", " ")

    col = re.sub(r"\(.*?\)", "", col)

    col = re.sub(r"\s+", " ", col).strip()

    col = col.title()

    return col


TIPOS_EXAME_FIXOS = [
    "Diagnostico Por Mamografia"
]

def extrair_tipos_exame() -> pd.DataFrame:
    df = pd.read_csv(DATASET_EXAMES, sep=";")

    colunas_exame = [
        c for c in df.columns
        if c not in COLUNAS_IGNORAR and df[c].dtype != object
    ]

    print("Colunas detectadas como exames:")
    for c in colunas_exame:
        print(" -", c)

    nomes_limpos = [limpar_nome_exame(c) for c in colunas_exame]

    nomes_limpos.extend(TIPOS_EXAME_FIXOS)

    df_out = pd.DataFrame({"nome_exame": nomes_limpos})
    
    df_out = df_out.drop_duplicates().sort_values("nome_exame").reset_index(drop=True)

    return df_out



def carregar_tipos_exame(conn, df_exames: pd.DataFrame):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT nome FROM tipo_exame;")
    existentes = {row["nome"] for row in cur.fetchall()}

    novas = []
    for _, row in df_exames.iterrows():
        nome = row["nome_exame"]
        if nome not in existentes:
            novas.append((nome, None))

    if novas:
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO tipo_exame (nome, descricao) VALUES %s;",
            novas
        )
        conn.commit()
        print(f"Foram inseridos {len(novas)} tipos de exame.")
    else:
        print("Nenhum tipo novo para inserir.")

    cur.close()


def main():
    print("Extraindo tipos de exame a partir dos nomes das colunas...")
    df_exames = extrair_tipos_exame()
    print(df_exames)

    conn = get_conn()
    try:
        carregar_tipos_exame(conn, df_exames)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
