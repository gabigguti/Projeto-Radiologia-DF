-- Tabela de unidades da federação
CREATE TABLE unidade_da_federacao (
    id_uf        SERIAL PRIMARY KEY,
    sigla        VARCHAR(2) NOT NULL,	
    nome         VARCHAR(100) NOT NULL
);

-- Tabela de regiões administrativas
CREATE TABLE regiao_administrativa (
    id_ra        SERIAL PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    id_uf        INTEGER      NOT NULL,
    CONSTRAINT fk_ra_uf
        FOREIGN KEY (id_uf)
        REFERENCES unidade_da_federacao (id_uf)
);

-- Tipos de exame (mamografia, raio X, etc.)
CREATE TABLE tipo_exame (
    id_tipo_exame  SERIAL PRIMARY KEY,
    nome           VARCHAR(100) NOT NULL,
    descricao      TEXT
);

-- Produção de exames por tipo, região e período
CREATE TABLE exame_realizado (
    id_exame                SERIAL PRIMARY KEY,
    id_tipo_exame           INTEGER   NOT NULL,
    id_uf                   INTEGER   NOT NULL,
    ano                     SMALLINT  NOT NULL,
    mes                     SMALLINT  NOT NULL,
    quantidade              INTEGER   NOT NULL,
    CONSTRAINT fk_exame_tipo
        FOREIGN KEY (id_tipo_exame)
        REFERENCES tipo_exame (id_tipo_exame),
    CONSTRAINT fk_exame_uf
        FOREIGN KEY (id_uf)
        REFERENCES unidade_da_federacao (id_uf)
);

-- Tipos de equipamento (mamógrafo, tomógrafo, etc.)
CREATE TABLE tipo_equipamento (
    id_tipo_equipamento  SERIAL PRIMARY KEY,
    nome                 VARCHAR(100) NOT NULL,
    descricao            TEXT,
    quantidade_publico   INTEGER   NOT NULL,
    quantidade_privado   INTEGER   NOT NULL,
    quantidade_funcionando_sus INTEGER NOT NULL,
    quantidade_parado_sus    INTEGER   NOT NULL
);

-- Registro agregado de equipamentos por RA e ano
CREATE TABLE equipamento_registrado (
    id_registro          SERIAL PRIMARY KEY,
    id_tipo_equipamento  INTEGER   NOT NULL,
    id_uf                INTEGER   NOT NULL,
    ano                  SMALLINT  NOT NULL,
    CONSTRAINT fk_equip_tipo
        FOREIGN KEY (id_tipo_equipamento)
        REFERENCES tipo_equipamento (id_tipo_equipamento),
    CONSTRAINT fk_equip_uf
        FOREIGN KEY (id_uf)
        REFERENCES unidade_da_federacao (id_uf)
);

-- População por região administrativa e ano
CREATE TABLE populacao (
    id_pop              SERIAL PRIMARY KEY,
    id_ra               INTEGER   NOT NULL,
    ano                 SMALLINT  NOT NULL,
    populacao_total     INTEGER   NOT NULL,
    populacao_plano_saude INTEGER NOT NULL,
    populacao_sem_plano_saude INTEGER NOT NULL,
    CONSTRAINT fk_pop_ra
        FOREIGN KEY (id_ra)
        REFERENCES regiao_administrativa (id_ra)
);

-- Categorias profissionais (técnico, auxiliar, radiologista etc.)
CREATE TABLE categoria_profissional (
    id_categoria  SERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    descricao     TEXT
);

-- Quantidade de profissionais por categoria, RA e ano
CREATE TABLE profissional_registrado (
    id_prof       SERIAL PRIMARY KEY,
    id_categoria  INTEGER   NOT NULL,
    id_uf         INTEGER   NOT NULL,
    ano           SMALLINT  NOT NULL,
    mes           SMALLINT  NOT NULL,
    quantidade    INTEGER   NOT NULL,
    CONSTRAINT fk_prof_cat
        FOREIGN KEY (id_categoria)
        REFERENCES categoria_profissional (id_categoria),
    CONSTRAINT fk_prof_uf
        FOREIGN KEY (id_uf)
        REFERENCES unidade_da_federacao (id_uf)
);

-- Páginas do portal (DataSUS, TABNET etc.)
CREATE TABLE pagina_portal (
    id_pagina  SERIAL PRIMARY KEY,
    nome       VARCHAR(150) NOT NULL,
    url        TEXT         NOT NULL,
    sistema    VARCHAR(100) NOT NULL
);

-- Métricas de acessibilidade WAVE por página e data de coleta
CREATE TABLE metrica_wave (
    id_wave        SERIAL PRIMARY KEY,
    id_pagina      INTEGER   NOT NULL,
    data_coleta    DATE      NOT NULL,
    errors         INTEGER   NOT NULL,
    contrast_errors INTEGER  NOT NULL,
    alerts         INTEGER   NOT NULL,
    aim_score      NUMERIC(4,2),
    CONSTRAINT fk_wave_pagina
        FOREIGN KEY (id_pagina)
        REFERENCES pagina_portal (id_pagina)
);

CREATE TABLE espera_exame (
    id_espera               SERIAL PRIMARY KEY,
    id_uf                   INTEGER NOT NULL,
    id_tipo_exame           INTEGER NOT NULL,
    ano                     SMALLINT NOT NULL,
    qtd_tempo_espera_0_10   INTEGER NOT NULL,
    qtd_tempo_espera_11_20  INTEGER NOT NULL,
    qtd_tempo_espera_21_30  INTEGER NOT NULL,
    qtd_tempo_espera_30_mais INTEGER NOT NULL,
    CONSTRAINT fk_espera_uf
        FOREIGN KEY (id_uf)
        REFERENCES unidade_da_federacao (id_uf),
    CONSTRAINT fk_espera_tipo
        FOREIGN KEY (id_tipo_exame)
        REFERENCES tipo_exame (id_tipo_exame),
    CONSTRAINT unq_espera_uf_exame_ano
        UNIQUE (id_uf, id_tipo_exame, ano)
);
