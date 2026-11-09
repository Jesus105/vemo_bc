-- Vemo · Business Case Growth Analyst · Esquema de datos crudos
-- Base: vemo. Un schema por case: impulso, conduce, watts.
--
-- Decisión de diseño: las tablas reflejan las hojas de Excel TAL CUAL (mismos nombres de columna).
-- No hay PRIMARY KEY, FOREIGN KEY ni CHECK a propósito: el LEEME dice que los datos "salen tal como
-- los exportan los sistemas", así que la carga no debe rechazar ni corregir filas. La validación y
-- limpieza son parte del análisis (sql/03_analytical_views.sql).
-- Los meses vienen como texto 'YYYY-MM' y así se conservan.

DROP SCHEMA IF EXISTS impulso CASCADE;
DROP SCHEMA IF EXISTS conduce CASCADE;
DROP SCHEMA IF EXISTS watts CASCADE;
CREATE SCHEMA impulso;
CREATE SCHEMA conduce;
CREATE SCHEMA watts;

-- Hojas LEEME y supuestos: mismas columnas en los tres cases.
-- valor viene mezclado (número o texto); valor_num es su versión numérica cuando aplica.
CREATE TABLE impulso.leeme (linea INTEGER GENERATED ALWAYS AS IDENTITY, texto TEXT);
CREATE TABLE conduce.leeme (LIKE impulso.leeme INCLUDING ALL);
CREATE TABLE watts.leeme   (LIKE impulso.leeme INCLUDING ALL);

CREATE TABLE impulso.supuestos (
    supuesto  TEXT,
    valor     TEXT,
    nota      TEXT,
    valor_num NUMERIC GENERATED ALWAYS AS (
        CASE WHEN valor ~ '^-?[0-9]+(\.[0-9]+)?$' THEN valor::NUMERIC END) STORED
);
CREATE TABLE conduce.supuestos (LIKE impulso.supuestos INCLUDING ALL);
CREATE TABLE watts.supuestos   (LIKE impulso.supuestos INCLUDING ALL);

-- ============================== Case 1 · Impulso ==============================
-- Funnel por mes calendario de cada evento (vista de Dirección).
CREATE TABLE impulso.funnel_mensual (
    mes                       TEXT,
    leads_creados             INTEGER,
    contactados               INTEGER,
    contactados_por_agente_ia INTEGER,
    enviados_a_analisis       INTEGER,
    rechazados_buro           INTEGER,
    rechazados_riesgo         INTEGER,
    calificados               INTEGER,
    dias_mediana_analisis     NUMERIC,
    visitas_aprobadas         INTEGER,
    entregas                  INTEGER
);

-- Funnel por cohorte de creación del lead (avance hasta la extracción, 4-nov-2026).
CREATE TABLE impulso.cohortes (
    mes_creacion                     TEXT,
    leads                            INTEGER,
    contactados                      INTEGER,
    enviados_a_analisis              INTEGER,
    calificados                      INTEGER,
    visitas_aprobadas                INTEGER,
    perdidos_en_visita_por_deposito  INTEGER,
    perdidos_en_visita_otros_motivos INTEGER,
    entregas_acumuladas              INTEGER,
    dias_mediana_lead_a_entrega      NUMERIC,
    leads_aun_en_proceso             INTEGER
);

CREATE TABLE impulso.canales (
    mes_creacion        TEXT,
    canal               TEXT,
    inversion_mxn       NUMERIC,
    leads               INTEGER,
    calificados         INTEGER,
    entregas_acumuladas INTEGER
);

-- ============================== Case 2 · Conduce ==============================
-- Una fila por firma. persona_id puede repetirse (recontrataciones). fecha_baja NULL = activo.
CREATE TABLE conduce.conductores (
    conductor_id          TEXT,
    persona_id            TEXT,
    fecha_firma           DATE,
    hub                   TEXT,
    turno                 TEXT,
    canal                 TEXT,
    distancia_casa_hub_km NUMERIC,
    horas_semanales_prom  NUMERIC,
    bono_semanal_prom_mxn NUMERIC,
    fecha_baja            DATE,
    motivo_baja           TEXT
);

CREATE TABLE conduce.hubs (
    hub            TEXT,
    zona           TEXT,
    autos          INTEGER,
    fecha_apertura DATE,
    fecha_cierre   DATE,
    nota           TEXT
);

CREATE TABLE conduce.cobertura_semanal (
    semana             DATE,
    hub                TEXT,
    turno              TEXT,
    turnos_disponibles INTEGER,
    turnos_cubiertos   INTEGER
);

CREATE TABLE conduce.funnel_mensual (
    mes                  TEXT,
    hub                  TEXT,
    turno                TEXT,
    leads                INTEGER,
    centro_de_carga      INTEGER,  -- etapa de filtro automático; NO es carga eléctrica
    revision             INTEGER,
    citados_induccion    INTEGER,
    asistieron_induccion INTEGER,
    firmas               INTEGER
);

CREATE TABLE conduce.inversion_mensual (
    mes           TEXT,
    canal         TEXT,
    inversion_mxn NUMERIC
);

-- ============================== Case 3 · Watts ================================
CREATE TABLE watts.hubs (
    hub_id                 TEXT,
    tipo                   TEXT,
    zona                   TEXT,
    fecha_apertura         DATE,
    conectores             INTEGER,
    potencia_kw            NUMERIC,
    precio_publico_kwh     NUMERIC,
    costo_energia_kwh      NUMERIC,
    costo_fijo_mensual_mxn NUMERIC,
    descuento_promo_agosto NUMERIC
);

CREATE TABLE watts.hub_mensual (
    mes                        TEXT,
    hub_id                     TEXT,
    dias_abierto               INTEGER,
    conectores_operativos_prom NUMERIC,
    horas_conector_disponibles NUMERIC,
    sesiones                   INTEGER,
    kwh                        NUMERIC,
    horas_conector_ocupadas    NUMERIC,
    ingreso_mxn                NUMERIC,
    costo_energia_mxn          NUMERIC
);

-- Índices para los cortes más comunes
CREATE INDEX ON conduce.conductores (hub, turno);
CREATE INDEX ON conduce.conductores (fecha_firma);
CREATE INDEX ON conduce.conductores (persona_id);
CREATE INDEX ON conduce.cobertura_semanal (hub, semana);
CREATE INDEX ON watts.hub_mensual (hub_id, mes);
