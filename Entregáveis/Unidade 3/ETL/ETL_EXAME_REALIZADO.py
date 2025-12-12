import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

CAMINHO_EXAMES = "dirty_data_qtd_mamografias_df.csv"  
NOME_EXAME_MAMOGRAFIA = "Diagnostico Por Mamografia" 

MAPA_MESES_EXTENSO = {
    "JANEIRO": 1,
    "FEVEREIRO": 2,
    "MARCO": 3,
    "ABRIL": 4,
    "MAIO": 5,
    "JUNHO": 6,
    "JULHO": 7,
    "AGOSTO": 8,
    "SETEMBRO": 9,
    "OUTUBRO": 10,
    "NOVEMBRO": 11,
    "DEZEMBRO": 12,
}


def parse_mes_ano(valor: str):
    if pd.isna(valor):
        return None, None

    valor = str(valor).strip()
    if "/" not in valor:
        return None, None

    mes_str, ano_str = valor.split("/", 1)
    mes_str = mes_str.strip().upper()
    ano_str = ano_str.strip()

    mes = MAPA_MESES_EXTENSO.get(mes_str)
    if mes is None:
        return None, None

    try:
        ano = int(ano_str)
    except ValueError:
        return None, None

    return ano, mes


def carregar_id_uf_df(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id_uf FROM unidade_da_federacao WHERE sigla = %s", ("DF",))
        row = cur.fetchone()
        if not row:
            raise RuntimeError("Não encontrei unidade_da_federacao com sigla = 'DF'.")
        return row[0]


def carregar_id_tipo_exame_mamografia(conn, nome_exame=NOME_EXAME_MAMOGRAFIA):
    with conn.cursor() as cur:
        cur.execute("SELECT id_tipo_exame FROM tipo_exame WHERE nome = %s", (nome_exame,))
        row = cur.fetchone()
        if not row:
            raise RuntimeError(
                f"Não encontrei tipo_exame com nome = '{nome_exame}'. "
                f"Verifique o nome de cadastro na tabela tipo_exame."
            )
        return row[0]


def normalizar_quantidade(valor):
    if pd.isna(valor):
        return None

    if isinstance(valor, str):
        valor = valor.strip()
        if valor == "":
            return None

    try:
        return int(float(valor))
    except (ValueError, TypeError):
        return None


def processar_dataset_exames(df, id_uf_df, id_tipo_exame):
    if "Mes/Ano" not in df.columns:
        raise RuntimeError("Coluna 'Mes/Ano' não encontrada no dataset de exames.")
    if "Exames" not in df.columns:
        raise RuntimeError("Coluna 'Exames' não encontrada no dataset de exames.")

    registros = []

    for _, row in df.iterrows():
        mes_ano_valor = row["Mes/Ano"]
        ano, mes = parse_mes_ano(mes_ano_valor)
        if ano is None or mes is None:
            continue

        quantidade = normalizar_quantidade(row["Exames"])
        if quantidade is None:
            continue

        registros.append((id_tipo_exame, mes, quantidade, id_uf_df, ano))

    return registros


def inserir_exames(conn, registros):
    if not registros:
        print("Nenhum registro para inserir em exame_realizado.")
        return

    sql = """
        INSERT INTO exame_realizado (id_tipo_exame, mes, quantidade, id_uf, ano)
        VALUES (%s, %s, %s, %s, %s);
    """

    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, registros, page_size=1000)
    conn.commit()
    print(f"Inseridos {len(registros)} registros em exame_realizado.")


def main():
    conn = get_conn()

    try:
        id_uf_df = carregar_id_uf_df(conn)
        id_tipo_exame_mamo = carregar_id_tipo_exame_mamografia(conn)

        print(f"id_uf para DF: {id_uf_df}")
        print(f"id_tipo_exame para {NOME_EXAME_MAMOGRAFIA}: {id_tipo_exame_mamo}")

        if not os.path.exists(CAMINHO_EXAMES):
            raise FileNotFoundError(f"Arquivo de exames não encontrado: {CAMINHO_EXAMES}")

        df = pd.read_csv(CAMINHO_EXAMES)
        print("Colunas encontradas no CSV de exames:", df.columns.tolist())

        registros = processar_dataset_exames(df, id_uf_df, id_tipo_exame_mamo)
        print(f"Registros gerados a partir do dataset de exames: {len(registros)}")

        inserir_exames(conn, registros)

    finally:
        conn.close()
        print("Conexão com o banco fechada.")


if __name__ == "__main__":
    main()
