import os
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv
from config_db import get_conn

load_dotenv()

DATASETS_PROFISSIONAIS = [
    {
        "caminho": "dirty_data_historico_anual_numero_medicos_radiologistas_e_diagnostico_imagem_SUS - cnes.csv",
        "coluna_periodo": "Ano/mês compet.",
        "colunas_ignorar": ["Ano/mês compet."],  
    },
    {
        "caminho": "dirty_data_historico_anual_numero_cirurgioes_dentistas_radiologistas_SUS - denstista_radio_profissinoais.csv",
        "coluna_periodo": "Ocupações de Nível Superior",
        "colunas_ignorar": ["Ocupações de Nível Superior"],  
    },
    {
        "caminho": "dirty_data_historico_anual_numero_auxiliares_e_tecnicos_em_radiologia_SUS.csv",
        "coluna_periodo": "Data",
        "colunas_ignorar": ["Data", "Total"],  
    },
]

MAPA_MESES = {
    "jan.": 1,
    "fev.": 2,
    "mar.": 3,
    "abr.": 4,
    "mai.": 5,
    "jun.": 6,
    "jul.": 7,
    "ago.": 8,
    "set.": 9,
    "out.": 10,
    "nov.": 11,
    "dez.": 12,
}


def parse_ano_mes(valor: str):
    if pd.isna(valor):
        return None, None

    valor = str(valor).strip()
    if "/" not in valor:
        return None, None

    ano_str, mes_str = valor.split("/", 1)
    ano_str = ano_str.strip()
    mes_str = mes_str.strip().lower()

    if not mes_str.endswith("."):
        mes_str = mes_str + "."

    try:
        ano = int(ano_str)
    except ValueError:
        return None, None

    mes = MAPA_MESES.get(mes_str)
    if mes is None:
        return None, None

    return ano, mes


def carregar_id_uf_df(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id_uf FROM unidade_da_federacao WHERE sigla = %s", ("DF",))
        row = cur.fetchone()
        if not row:
            raise RuntimeError("Não encontrei unidade_da_federacao com sigla = 'DF'.")
        return row[0]


def carregar_mapa_categorias(conn):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT id_categoria, nome FROM categoria_profissional;")
        linhas = cur.fetchall()

    mapa = {}
    for linha in linhas:
        nome = linha["nome"].strip()
        mapa[nome] = linha["id_categoria"]

    return mapa


def normalizar_quantidade(valor):
    if pd.isna(valor):
        return None

    # Alguns CSVs podem vir como string, vamos limpar espaços
    if isinstance(valor, str):
        valor = valor.strip()
        if valor == "":
            return None

    try:
        # Muitos desses dados são inteiros mesmo
        return int(float(valor))
    except (ValueError, TypeError):
        return None


def processar_dataset(df, config, id_uf_df, mapa_categorias):
    col_periodo = config["coluna_periodo"]
    colunas_ignorar = config["colunas_ignorar"]

    if col_periodo not in df.columns:
        raise RuntimeError(f"Coluna de período '{col_periodo}' não encontrada no dataset {config['caminho']}")

    registros = []

    colunas_categoria = [c for c in df.columns if c not in colunas_ignorar]

    for _, row in df.iterrows():
        periodo_valor = row[col_periodo]
        ano, mes = parse_ano_mes(periodo_valor)
        if ano is None or mes is None:
            continue

        for coluna_cat in colunas_categoria:
            nome_categoria = coluna_cat.strip()
            id_categoria = mapa_categorias.get(nome_categoria)

            if id_categoria is None:
                print(f"[AVISO] Categoria '{nome_categoria}' não encontrada em categoria_profissional. Linha ignorada.")
                continue

            quantidade = normalizar_quantidade(row[coluna_cat])
            if quantidade is None:
                continue

            registros.append((id_categoria, id_uf_df, ano, mes, quantidade))

    return registros


def inserir_profissionais(conn, registros):
    if not registros:
        print("Nenhum registro para inserir em profissional_registrado.")
        return

    sql = """
        INSERT INTO profissional_registrado (id_categoria, id_uf, ano, mes, quantidade)
        VALUES (%s, %s, %s, %s, %s);
    """

    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, registros, page_size=1000)
    conn.commit()
    print(f"Inseridos {len(registros)} registros em profissional_registrado.")


def main():
    conn = get_conn()

    try:
        id_uf_df = carregar_id_uf_df(conn)
        mapa_categorias = carregar_mapa_categorias(conn)

        print(f"id_uf para DF: {id_uf_df}")
        print(f"Categorias carregadas: {len(mapa_categorias)}")

        registros_totais = []

        for config in DATASETS_PROFISSIONAIS:
            caminho = config["caminho"]
            print(f"\nProcessando dataset: {caminho}")

            if not os.path.exists(caminho):
                raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

            df = pd.read_csv(caminho)

            registros = processar_dataset(df, config, id_uf_df, mapa_categorias)
            print(f"Registros gerados a partir de {caminho}: {len(registros)}")
            registros_totais.extend(registros)

        inserir_profissionais(conn, registros_totais)

    finally:
        conn.close()
        print("Conexão com o banco fechada.")


if __name__ == "__main__":
    main()
