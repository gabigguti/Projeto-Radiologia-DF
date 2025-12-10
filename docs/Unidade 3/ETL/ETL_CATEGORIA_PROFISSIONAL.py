import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

DATASETS_PROF = [
    "dirty_data_historico_anual_numero_auxiliares_e_tecnicos_em_radiologia_SUS.csv",
    "dirty_data_historico_anual_numero_cirurgioes_dentistas_radiologistas_SUS - denstista_radio_profissinoais.csv",
    "dirty_data_historico_anual_numero_medicos_radiologistas_e_diagnostico_imagem_SUS - cnes.csv",
]

COLUNAS_NAO_CATEGORIA = [
    "Ocupações de Nível Superior",
    "Data",
    "Total",
    "Ano/mês compet.",
]

def extrair_categorias_dos_datasets() -> list[str]:
    categorias = set()

    for caminho in DATASETS_PROF:
        if not os.path.exists(caminho):
            print(f"Aviso: arquivo nao encontrado, pulando: {caminho}")
            continue

        df = pd.read_csv(caminho, sep=",")

        print(f"\nLendo colunas de: {caminho}")
        print("Colunas encontradas:", list(df.columns))

        colunas_excluir = {c.strip().lower() for c in COLUNAS_NAO_CATEGORIA}

        for col in df.columns:
            col_normal = col.strip()

            if col_normal.lower() in colunas_excluir:
                continue  
                
            if not col_normal:
                continue  

            categorias.add(col_normal)

    categorias = sorted(categorias)
    print("\nCategorias identificadas:")
    for c in categorias:
        print("  -", c)

    return categorias


def carregar_categorias_profissionais(conn, categorias: list[str]) -> None:
    if not categorias:
        print("Nenhuma categoria encontrada.")
        return

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT nome FROM categoria_profissional;")
    existentes = {row["nome"].strip().lower() for row in cur.fetchall()}

    novas = []
    for cat in categorias:
        chave = cat.lower()
        if chave not in existentes:
            novas.append((cat,))

    if not novas:
        print("Nenhuma nova categoria para inserir.")
    else:
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO categoria_profissional (nome) VALUES %s;",
            novas
        )
        conn.commit()
        print(f"Foram inseridas {len(novas)} novas categorias profissionais.")

    cur.close()


def main():
    print("Extraindo categorias profissionais...")
    categorias = extrair_categorias_dos_datasets()

    conn = get_conn()
    try:
        print("\nInserindo categorias na tabela categoria_profissional...")
        carregar_categorias_profissionais(conn, categorias)
        print("\nETL de categorias profissionais concluído.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
