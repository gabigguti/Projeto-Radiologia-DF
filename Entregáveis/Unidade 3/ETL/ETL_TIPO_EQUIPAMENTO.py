import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

DATASET_EQUIP_TIPO = "dirty_data_qtd_equip_img_SUS_por_tipo.csv"


def tratar_dataset_tipo_equipamento() -> pd.DataFrame:
    if not os.path.exists(DATASET_EQUIP_TIPO):
        raise FileNotFoundError(f"Arquivo nao encontrado: {DATASET_EQUIP_TIPO}")

    df = pd.read_csv(DATASET_EQUIP_TIPO)

    colunas_esperadas = [
        "codigo",
        "equipamento",
        "existentes",
        "em_uso",
        "existentes_SUS",
        "em_uso_SUS",
    ]
    for c in colunas_esperadas:
        if c not in df.columns:
            raise ValueError(f"Coluna '{c}' nao encontrada no CSV. Colunas: {df.columns}")

    df["nome"] = df["equipamento"].astype(str).str.strip()

    df["existentes"] = pd.to_numeric(df["existentes"], errors="coerce").fillna(0).astype(int)
    df["existentes_SUS"] = pd.to_numeric(df["existentes_SUS"], errors="coerce").fillna(0).astype(int)
    df["em_uso_SUS"] = pd.to_numeric(df["em_uso_SUS"], errors="coerce").fillna(0).astype(int)

    df["existentes"] = df["existentes"].clip(lower=0)
    df["existentes_SUS"] = df["existentes_SUS"].clip(lower=0)
    df["em_uso_SUS"] = df["em_uso_SUS"].clip(lower=0)

    df["quantidade_publico"] = df["existentes_SUS"]
    df["quantidade_privado"] = (df["existentes"] - df["existentes_SUS"]).clip(lower=0)
    df["quantidade_funcionando_publico"] = df["em_uso_SUS"]
    df["quantidade_parado_publico"] = (df["existentes_SUS"] - df["em_uso_SUS"]).clip(lower=0)

    df_out = df[
        [
            "nome",
            "quantidade_publico",
            "quantidade_privado",
            "quantidade_funcionando_publico",
            "quantidade_parado_publico",
        ]
    ].copy()

    return df_out


def carregar_tipo_equipamento(conn, df: pd.DataFrame) -> None:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT id_tipo_equipamento, nome FROM tipo_equipamento;")
    rows = cur.fetchall()
    existentes = {str(r["nome"]).strip().lower(): r["id_tipo_equipamento"] for r in rows}

    insercoes = []
    atualizacoes = []

    for _, row in df.iterrows():
        nome = row["nome"].strip()
        chave = nome.lower()

        q_pub = int(row["quantidade_publico"])
        q_priv = int(row["quantidade_privado"])
        q_func = int(row["quantidade_funcionando_publico"])
        q_parado = int(row["quantidade_parado_publico"])

        if chave in existentes:
            id_tipo = existentes[chave]
            atualizacoes.append(
                (
                    q_pub,
                    q_priv,
                    q_func,
                    q_parado,
                    id_tipo,
                )
            )
        else:
            insercoes.append(
                (
                    nome,
                    None,  
                    q_pub,
                    q_priv,
                    q_func,
                    q_parado,
                )
            )

    if insercoes:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO tipo_equipamento
            (nome, descricao, quantidade_publico, quantidade_privado,
             quantidade_funcionando_sus, quantidade_parado_sus)
            VALUES %s
            """,
            insercoes,
        )
        print(f"Foram inseridos {len(insercoes)} novos tipos de equipamento.")

    if atualizacoes:
        cur.executemany(
            """
            UPDATE tipo_equipamento
            SET quantidade_publico = %s,
                quantidade_privado = %s,
                quantidade_funcionando_sus = %s,
                quantidade_parado_sus = %s
            WHERE id_tipo_equipamento = %s
            """,
            atualizacoes,
        )
        print(f"Foram atualizados {len(atualizacoes)} tipos de equipamento existentes.")

    conn.commit()
    cur.close()


def main():
    print("Lendo e tratando dataset de equipamentos por tipo (nivel DF)...")
    df = tratar_dataset_tipo_equipamento()
    print(f"Total de linhas no dataset: {len(df)}")

    conn = get_conn()
    try:
        carregar_tipo_equipamento(conn, df)
        print("ETL de tipo_equipamento concluido com sucesso.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
