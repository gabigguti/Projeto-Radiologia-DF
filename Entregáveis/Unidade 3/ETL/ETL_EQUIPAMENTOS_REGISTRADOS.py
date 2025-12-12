import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

DATASET_EQUIP_RA = "dirty_data_distribuição_geo_equipamentos.csv"

ANO_PADRAO = 2025

MAPEAMENTO_COLUNAS_EQUIP = {
    "qtd_gama_camara": "Gama Câmara",
    "qtd_mamografo_comando_simples": "Mamógrafo com Comando Simples",
    "qtd_mamografo_estereotaxia": "Mamógrafo com Estereotaxia",
    "qtd_raio_X_100_mA": "Raio X ate 100 mA",
    "qtd_raio_X_100_500_mA": "Raio X de 100 a 500 mA",
    "qtd_raio_X_mais_500_mA": "Raio X mais de 500mA",
    "qtd_raio_X_dentario": "Raio X Dentário",
    "qtd_raio_X_fluoroscopia": "Raio X com Fluoroscopia",
    "qtd_raio_X_densitometria_ossea": "Raio X para Densitometria Óssea",
    "qtd_raio_X_hemodinamica": "Raio X para Hemodinâmica",
    "qtd_tomografo_computadorizado": "Tomógrafo Computadorizado",
    "qtd_ressonancia_magnetica": "Ressonância Magnética",
    "qtd_ultrassom_doppler_colorido": "Ultrassom Doppler Colorido",
    "qtd_ultrassom_ecografo": "Ultrassom Ecógrafo",
    "qtd_ultrassom_convencional": "Ultrassom Convencional",
    "qtd_processadora_de_filme_mamografia": "Processadora De Filme Mamografia",
    "qtd_mamografo_computadorizado": "Mamógrafo Computadorizado",
    "qtd_pet_ct": "PET/CT",
}


def limpar_nome_ra(nome: str) -> str:
    if not isinstance(nome, str):
        return None
    n = nome.strip()
    if not n:
        return None
    return n.title()


def tratar_dataset_equipamento_por_ra() -> pd.DataFrame:
    if not os.path.exists(DATASET_EQUIP_RA):
        raise FileNotFoundError(f"Arquivo nao encontrado: {DATASET_EQUIP_RA}")

    df = pd.read_csv(DATASET_EQUIP_RA)

    if "ra" not in df.columns:
        raise ValueError(f"Coluna 'ra' nao encontrada. Colunas: {df.columns}")

    for col in MAPEAMENTO_COLUNAS_EQUIP.keys():
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' do mapeamento nao existe no CSV. Colunas: {df.columns}")

    df["nome_ra"] = df["ra"].astype(str).apply(limpar_nome_ra)

    registros = []

    for _, row in df.iterrows():
        nome_ra = row["nome_ra"]
        if not nome_ra:
            continue

        for col_csv, nome_tipo in MAPEAMENTO_COLUNAS_EQUIP.items():
            valor = row[col_csv]

            try:
                qtd = int(valor)
            except (ValueError, TypeError):
                continue

            if qtd <= 0:
                continue

            registros.append(
                {
                    "nome_ra": nome_ra,
                    "nome_equipamento": nome_tipo,
                    "quantidade": qtd,
                    "ano": ANO_PADRAO,
                }
            )

    df_out = pd.DataFrame(registros)
    return df_out


def mapear_ids(conn, df: pd.DataFrame) -> pd.DataFrame:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT id_ra, nome FROM regiao_administrativa;")
    mapa_ra = {str(r["nome"]).strip().lower(): r["id_ra"] for r in cur.fetchall()}

    cur.execute("SELECT id_tipo_equipamento, nome FROM tipo_equipamento;")
    mapa_tipo = {str(r["nome"]).strip().lower(): r["id_tipo_equipamento"] for r in cur.fetchall()}

    cur.close()

    def get_id_ra(nome):
        if not isinstance(nome, str):
            return None
        return mapa_ra.get(nome.strip().lower())

    def get_id_tipo(nome):
        if not isinstance(nome, str):
            return None
        return mapa_tipo.get(nome.strip().lower())

    df["id_ra"] = df["nome_ra"].apply(get_id_ra)
    df["id_tipo_equipamento"] = df["nome_equipamento"].apply(get_id_tipo)

    ras_erradas = df[df["id_ra"].isna()]["nome_ra"].unique()
    if len(ras_erradas) > 0:
        print("RAs nao encontradas em regiao_administrativa:")
        for n in ras_erradas:
            print("  ", n)

    tipos_errados = df[df["id_tipo_equipamento"].isna()]["nome_equipamento"].unique()
    if len(tipos_errados) > 0:
        print("Tipos de equipamento nao encontrados em tipo_equipamento:")
        for n in tipos_errados:
            print("  ", n)

    df_ok = df.dropna(subset=["id_ra", "id_tipo_equipamento"]).copy()
    df_ok["id_ra"] = df_ok["id_ra"].astype(int)
    df_ok["id_tipo_equipamento"] = df_ok["id_tipo_equipamento"].astype(int)
    df_ok["quantidade"] = df_ok["quantidade"].astype(int)
    df_ok["ano"] = df_ok["ano"].astype(int)

    return df_ok


def carregar_equipamento_registrado(conn, df: pd.DataFrame) -> None:
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    linhas = [
        (
            int(row["id_tipo_equipamento"]),
            int(row["id_ra"]),
            int(row["ano"]),
            int(row["quantidade"]),
        )
        for _, row in df.iterrows()
    ]

    if not linhas:
        print("Nenhuma linha para inserir em equipamento_registrado.")
        return

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO equipamento_registrado
        (id_tipo_equipamento, id_ra, ano, quantidade)
        VALUES %s
        """,
        linhas,
    )
    conn.commit()
    cur.close()

    print(f"Foram inseridos {len(linhas)} registros em equipamento_registrado.")


def main():
    print("Lendo e tratando dataset de equipamentos por RA...")
    df = tratar_dataset_equipamento_por_ra()
    print(f"Total de linhas apos tratamento: {len(df)}")

    conn = get_conn()
    try:
        print("Mapeando ids de RA e tipo de equipamento...")
        df_map = mapear_ids(conn, df)
        print(f"Total de linhas apos mapeamento: {len(df_map)}")

        print("Inserindo registros em equipamento_registrado...")
        carregar_equipamento_registrado(conn, df_map)

        print("ETL de equipamento_registrado concluido.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
