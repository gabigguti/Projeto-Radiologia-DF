-- Tabela de unidades da federação
CREATE TABLE unidade_da_federacao (
    id_uf        SERIAL PRIMARY KEY,
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
    id_ra                   INTEGER   NOT NULL,
    ano                     DATE  NOT NULL,
    mes                     SMALLINT  NOT NULL,
    quantidade              INTEGER   NOT NULL,
    tempo_espera_categoria1 NUMERIC(5,2),
    tempo_espera_categoria2 NUMERIC(5,2),
    tempo_espera_categoria3 NUMERIC(5,2),
    tempo_espera_categoria4 NUMERIC(5,2),
    CONSTRAINT fk_exame_tipo
        FOREIGN KEY (id_tipo_exame)
        REFERENCES tipo_exame (id_tipo_exame),
    CONSTRAINT fk_exame_ra
        FOREIGN KEY (id_ra)
        REFERENCES regiao_administrativa (id_ra)
);

-- Tipos de equipamento (mamógrafo, tomógrafo, etc.)
CREATE TABLE tipo_equipamento (
    id_tipo_equipamento  SERIAL PRIMARY KEY,
    nome                 VARCHAR(100) NOT NULL,
    descricao            TEXT
);

-- Registro agregado de equipamentos por RA e ano
CREATE TABLE equipamento_registrado (
    id_registro          SERIAL PRIMARY KEY,
    id_tipo_equipamento  INTEGER   NOT NULL,
    id_ra                INTEGER   NOT NULL,
    ano                  SMALLINT  NOT NULL,
    quantidade_publico   INTEGER   NOT NULL,
    quantidade_privado   INTEGER   NOT NULL,
    quantidade_funcionando INTEGER NOT NULL,
    quantidade_parado    INTEGER   NOT NULL,
    CONSTRAINT fk_equip_tipo
        FOREIGN KEY (id_tipo_equipamento)
        REFERENCES tipo_equipamento (id_tipo_equipamento),
    CONSTRAINT fk_equip_ra
        FOREIGN KEY (id_ra)
        REFERENCES regiao_administrativa (id_ra)
);

-- População por região administrativa e ano
CREATE TABLE populacao (
    id_pop              SERIAL PRIMARY KEY,
    id_ra               INTEGER   NOT NULL,
    ano                 SMALLINT  NOT NULL,
    populacao_total     INTEGER   NOT NULL,
    populacao_plano_saude INTEGER NOT NULL,
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
    id_ra         INTEGER   NOT NULL,
    ano           DATE  NOT NULL,
    quantidade    INTEGER   NOT NULL,
    CONSTRAINT fk_prof_cat
        FOREIGN KEY (id_categoria)
        REFERENCES categoria_profissional (id_categoria),
    CONSTRAINT fk_prof_ra
        FOREIGN KEY (id_ra)
        REFERENCES regiao_administrativa (id_ra)
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

