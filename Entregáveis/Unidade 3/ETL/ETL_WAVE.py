import os
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

DATASET_PATH = "dirty_data_dataset_usabilidade_dataSUS_WAVE.csv"

DATA_COLETA_FIXA = "2025-11-16"

def classificar_sistema(url: str) -> str:
    if not isinstance(url, str):
        return "DATASUS"

    url_lower = url.lower()

    if "?cnes" in url_lower:
        return "CNES"
    if "?ibge" in url_lower:
        return "IBGE"
    if "?pnad" in url_lower:
        return "IPEDF"
    if "?siscan" in url_lower:
        return "SISCAN"
    return "DATASUS"


def tratar_dataset_wave(caminho_csv: str) -> pd.DataFrame:

    df = pd.read_csv(caminho_csv, skiprows=2)


    df.columns = df.columns.str.strip()
    
    df = df.rename(
        columns={
            "Links": "url",
            "Errors": "errors",
            "Contrast Errors": "contrast_errors",
            "Alerts": "alerts",
            "AIM Score": "aim_score",
        }
    )

    colunas_interesse = ["url", "errors", "contrast_errors", "alerts", "aim_score"]
    df = df[colunas_interesse].copy()

    df["url"] = df["url"].astype(str).str.strip()

    df["sistema"] = df["url"].apply(classificar_sistema)

    for col in ["errors", "contrast_errors", "alerts"]:

        df[col] = pd.to_numeric(df[col], errors="coerce")

        df[col] = df[col].fillna(0)

        df[col] = np.where(df[col] < 0, 0, df[col])

        df[col] = np.floor(df[col]).astype(int)

    df["aim_score"] = pd.to_numeric(df["aim_score"], errors="coerce")

    return df


def carregar_paginas(conn, df_wave: pd.DataFrame) -> None:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT id_pagina, url FROM pagina_portal;")
    existentes = cur.fetchall()
    urls_existentes = {row["url"]: row["id_pagina"] for row in existentes}

    novas_linhas = []
    for _, row in df_wave.drop_duplicates(subset=["url"]).iterrows():
        url = row["url"]
        sistema = row["sistema"]
        if url not in urls_existentes:
            nome = url
            novas_linhas.append((nome, url, sistema))

    if novas_linhas:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO pagina_portal (nome, url, sistema)
            VALUES %s
            """,
            novas_linhas,
        )
        conn.commit()
        print(f"Foram inseridas {len(novas_linhas)} novas paginas em pagina_portal.")
    else:
        print("Nenhuma nova pagina para inserir em pagina_portal.")

    cur.close()


def carregar_metricas_wave(conn, df_wave: pd.DataFrame) -> None:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT id_pagina, url FROM pagina_portal;")
    paginas = cur.fetchall()
    mapa_url_id = {row["url"]: row["id_pagina"] for row in paginas}

    linhas_metricas = []
    urls_sem_id = set()

    for _, row in df_wave.iterrows():
        url = row["url"]
        id_pagina = mapa_url_id.get(url)

        if id_pagina is None:
            urls_sem_id.add(url)
            continue

        linha = (
            id_pagina,
            DATA_COLETA_FIXA,
            int(row["errors"]) if not pd.isna(row["errors"]) else 0,
            int(row["contrast_errors"])
            if not pd.isna(row["contrast_errors"])
            else 0,
            int(row["alerts"]) if not pd.isna(row["alerts"]) else 0,
            float(row["aim_score"]) if not pd.isna(row["aim_score"]) else None,
        )
        linhas_metricas.append(linha)

    if urls_sem_id:
        print("Atencao: existem URLs sem id_pagina mapeado em pagina_portal:")
        for u in urls_sem_id:
            print(" -", u)

    if linhas_metricas:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO metrica_wave
                (id_pagina, data_coleta, errors, contrast_errors, alerts, aim_score)
            VALUES %s
            """,
            linhas_metricas,
        )
        conn.commit()
        print(f"Foram inseridos {len(linhas_metricas)} registros em metrica_wave.")
    else:
        print("Nenhuma metrica para inserir em metrica_wave.")

    cur.close()


def main():
    print("Lendo e tratando dataset WAVE...")
    df_wave = tratar_dataset_wave(DATASET_PATH)

    conn = get_conn()
    try:
        print("Carregando paginas...")
        carregar_paginas(conn, df_wave)

        print("Carregando metricas WAVE...")
        carregar_metricas_wave(conn, df_wave)

        print("ETL WAVE concluido com sucesso.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
