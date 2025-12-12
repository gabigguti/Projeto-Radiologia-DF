import psycopg2
import psycopg2.extras
from config_db import get_conn

UFS = [
    ("Acre", "AC"),
    ("Alagoas", "AL"),
    ("Amapá", "AP"),
    ("Amazonas", "AM"),
    ("Bahia", "BA"),
    ("Ceará", "CE"),
    ("Distrito Federal", "DF"),
    ("Espírito Santo", "ES"),
    ("Goiás", "GO"),
    ("Maranhão", "MA"),
    ("Mato Grosso", "MT"),
    ("Mato Grosso do Sul", "MS"),
    ("Minas Gerais", "MG"),
    ("Pará", "PA"),
    ("Paraíba", "PB"),
    ("Paraná", "PR"),
    ("Pernambuco", "PE"),
    ("Piauí", "PI"),
    ("Rio de Janeiro", "RJ"),
    ("Rio Grande do Norte", "RN"),
    ("Rio Grande do Sul", "RS"),
    ("Rondônia", "RO"),
    ("Roraima", "RR"),
    ("Santa Catarina", "SC"),
    ("São Paulo", "SP"),
    ("Sergipe", "SE"),
    ("Tocantins", "TO"),
]


def carregar_ufs(conn):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT sigla FROM unidade_da_federacao;")
    existentes = {row["sigla"] for row in cur.fetchall()}

    novas_linhas = []
    for nome, sigla in UFS:
        if sigla not in existentes:
            novas_linhas.append((nome, sigla))

    if novas_linhas:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO unidade_da_federacao (nome, sigla)
            VALUES %s
            """,
            novas_linhas,
        )
        conn.commit()
        print(f"Foram inseridas {len(novas_linhas)} novas UFs.")
    else:
        print("Nenhuma UF nova para inserir.")

    cur.close()


def main():
    conn = get_conn()
    try:
        carregar_ufs(conn)
        print("ETL de UFs concluído.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
