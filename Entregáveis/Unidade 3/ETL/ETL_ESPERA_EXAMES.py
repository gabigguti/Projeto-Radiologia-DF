import os
import glob
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

BASE_DIR = "dirty_data_estados_espera_mamografia" 

NOME_EXAME = "Diagnostico Por Mamografia"


def extrair_sigla_uf_do_arquivo(caminho_arquivo: str) -> str:
    nome = os.path.basename(caminho_arquivo).lower()

    if not nome.startswith("mamografia_atend") or not nome.endswith(".csv"):
        raise ValueError(f"Nome de arquivo fora do padrao esperado: {nome}")

    meio = nome.replace("mamografia_atend", "").replace(".csv", "")

    if len(meio) != 2:
        raise ValueError(f"Sigla de UF invalida no arquivo: {nome}")

    return meio.upper()


def extrair_espera_de_arquivo(caminho_csv: str) -> pd.DataFrame:
    df = pd.read_csv(caminho_csv, sep=";")

    df.columns = df.columns.str.strip()

    col_ano = "Ano Resultado"
    col_0_10 = "0 - 10 dias"
    col_11_20 = "11 - 20 dias"
    col_21_30 = "21 - 30 dias"
    col_30_mais = "> 30 dias"

    colunas_faltando = [
        c
        for c in [col_ano, col_0_10, col_11_20, col_21_30, col_30_mais]
        if c not in df.columns
    ]
    if colunas_faltando:
        raise ValueError(
            f"Colunas nao encontradas no CSV {caminho_csv}: {colunas_faltando}. "
            f"Colunas disponiveis: {list(df.columns)}"
        )

    df_pad = df[[col_ano, col_0_10, col_11_20, col_21_30, col_30_mais]].copy()

    df_pad = df_pad.rename(
        columns={
            col_ano: "ano",
            col_0_10: "qtd_0_10",
            col_11_20: "qtd_11_20",
            col_21_30: "qtd_21_30",
            col_30_mais: "qtd_30_mais",
        }
    )

    df_pad["ano"] = pd.to_numeric(df_pad["ano"], errors="coerce").astype("Int64")

    for col in ["qtd_0_10", "qtd_11_20", "qtd_21_30", "qtd_30_mais"]:
        df_pad[col] = pd.to_numeric(df_pad[col], errors="coerce").fillna(0)
        df_pad[col] = df_pad[col].clip(lower=0)
        df_pad[col] = df_pad[col].astype(int)

    df_pad = df_pad.dropna(subset=["ano"])

    return df_pad


def obter_id_uf_por_sigla(conn, sigla: str) -> int:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT id_uf FROM unidade_da_federacao WHERE sigla = %s;",
        (sigla,),
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        raise ValueError(f"Nao foi encontrado registro de UF com sigla '{sigla}'.")
    return row["id_uf"]


def obter_id_tipo_exame(conn, nome_exame: str) -> int:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT id_tipo_exame FROM tipo_exame WHERE lower(nome) = lower(%s);",
        (nome_exame,),
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        raise ValueError(f"Nao foi encontrado tipo_exame com nome '{nome_exame}'.")
    return row["id_tipo_exame"]


def carregar_espera_exame(
    conn,
    df_espera: pd.DataFrame,
    id_uf: int,
    id_tipo_exame: int,
    sigla_uf: str,
) -> None:

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    valores = []
    for _, row in df_espera.iterrows():
        ano = int(row["ano"])
        v0_10 = int(row["qtd_0_10"])
        v11_20 = int(row["qtd_11_20"])
        v21_30 = int(row["qtd_21_30"])
        v30_mais = int(row["qtd_30_mais"])

        valores.append((id_uf, id_tipo_exame, ano, v0_10, v11_20, v21_30, v30_mais))

    if not valores:
        print(f"Nenhum dado de espera para inserir para UF {sigla_uf}.")
        cur.close()
        return

    query = """
        INSERT INTO espera_exame (
            id_uf,
            id_tipo_exame,
            ano,
            qtd_tempo_espera_0_10,
            qtd_tempo_espera_11_20,
            qtd_tempo_espera_21_30,
            qtd_tempo_espera_30_mais
        )
        VALUES %s
        ON CONFLICT (id_uf, id_tipo_exame, ano)
        DO UPDATE SET
            qtd_tempo_espera_0_10   = EXCLUDED.qtd_tempo_espera_0_10,
            qtd_tempo_espera_11_20  = EXCLUDED.qtd_tempo_espera_11_20,
            qtd_tempo_espera_21_30  = EXCLUDED.qtd_tempo_espera_21_30,
            qtd_tempo_espera_30_mais = EXCLUDED.qtd_tempo_espera_30_mais;
    """

    psycopg2.extras.execute_values(cur, query, valores)
    conn.commit()
    cur.close()

    print(f"Foram inseridos ou atualizados {len(valores)} registros para UF {sigla_uf}.")


def main():
    padrao = os.path.join(BASE_DIR, "mamografia_atend*.csv")
    arquivos = sorted(glob.glob(padrao))

    if not arquivos:
        print(f"Nenhum arquivo encontrado com padrao {padrao}")
        return

    print("Arquivos encontrados:")
    for a in arquivos:
        print(" ", os.path.basename(a))

    conn = get_conn()

    try:
        id_tipo = obter_id_tipo_exame(conn, NOME_EXAME)

        for arquivo in arquivos:
            try:
                sigla = extrair_sigla_uf_do_arquivo(arquivo)
                print(f"\nProcessando arquivo {os.path.basename(arquivo)} para UF {sigla}...")

                id_uf = obter_id_uf_por_sigla(conn, sigla)
                df_esp = extrair_espera_de_arquivo(arquivo)

                carregar_espera_exame(conn, df_esp, id_uf, id_tipo, sigla)

            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")

        print("\nETL de espera_exame concluido para todos os arquivos.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
