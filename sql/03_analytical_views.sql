-- Vemo · Vistas analíticas (las tablas crudas no se tocan; todo supuesto va comentado)
-- Ejecutar: docker exec -i vemo-postgres psql -U postgres -d vemo < sql/03_analytical_views.sql

------------------------------------------------------------------ IMPULSO
-- Funnel calendario (vista de Dirección) con tasas por etapa y bandera pre/post agente IA (1-may-2026).
-- Noviembre se marca incompleto (extracción 4-nov).
CREATE OR REPLACE VIEW impulso.v_funnel_tasas AS
SELECT mes,
       CASE WHEN mes < '2026-05' THEN 'pre_agente' ELSE 'post_agente' END AS periodo,
       mes = '2026-11' AS mes_incompleto,
       leads_creados, contactados, enviados_a_analisis, rechazados_buro, rechazados_riesgo,
       calificados, visitas_aprobadas, entregas, dias_mediana_analisis,
       round(contactados::numeric / leads_creados, 3)            AS tasa_contacto,
       round(enviados_a_analisis::numeric / contactados, 3)      AS tasa_envio,
       round(calificados::numeric / enviados_a_analisis, 3)      AS tasa_aprobacion,
       round(rechazados_riesgo::numeric / enviados_a_analisis, 3) AS tasa_rechazo_riesgo,
       enviados_a_analisis - 700                                  AS envios_sobre_capacidad, -- capacidad Riesgo = 700/mes
       round(entregas::numeric / leads_creados, 4)               AS lead_a_entrega_calendario
FROM impulso.funnel_mensual;

-- Funnel por cohorte (mes de creación). Cohortes oct/nov siguen abiertas: no comparables.
CREATE OR REPLACE VIEW impulso.v_cohortes_tasas AS
SELECT mes_creacion,
       CASE WHEN mes_creacion < '2026-05' THEN 'pre_agente' ELSE 'post_agente' END AS periodo,
       leads_aun_en_proceso > 0.05 * leads AS cohorte_abierta,
       leads, enviados_a_analisis, calificados, visitas_aprobadas, entregas_acumuladas,
       perdidos_en_visita_por_deposito, perdidos_en_visita_otros_motivos,
       round(entregas_acumuladas::numeric / leads, 4)              AS lead_a_entrega,
       round(calificados::numeric / enviados_a_analisis, 3)        AS aprobacion,
       round(entregas_acumuladas::numeric / calificados, 3)        AS calificado_a_entrega,
       round(perdidos_en_visita_por_deposito::numeric / nullif(visitas_aprobadas, 0), 3) AS perdida_deposito
FROM impulso.cohortes;

-- Exceso de rechazos de Riesgo atribuible al agente: rechazos por encima de la tasa pre-agente (ene–abr).
-- Supuesto: el exceso = leads que no cumplen requisitos mínimos (Riesgo siempre los rechaza).
CREATE OR REPLACE VIEW impulso.v_exceso_riesgo AS
WITH base AS (
  SELECT sum(rechazados_riesgo)::numeric / sum(enviados_a_analisis) AS tasa_pre
  FROM impulso.funnel_mensual WHERE mes < '2026-05')
SELECT f.mes, f.enviados_a_analisis, f.rechazados_riesgo,
       round(f.enviados_a_analisis * b.tasa_pre)                           AS riesgo_esperado,
       f.rechazados_riesgo - round(f.enviados_a_analisis * b.tasa_pre)     AS exceso_riesgo,
       (f.rechazados_riesgo - round(f.enviados_a_analisis * b.tasa_pre)) * 180 AS costo_exceso_mxn
FROM impulso.funnel_mensual f CROSS JOIN base b
WHERE f.mes BETWEEN '2026-05' AND '2026-10';

-- Canales: CPL, CAC (inversión / entregas acumuladas), sólo cohortes cerradas (ene–sep).
CREATE OR REPLACE VIEW impulso.v_canales_cac AS
SELECT canal,
       sum(inversion_mxn) AS inversion, sum(leads) AS leads, sum(entregas_acumuladas) AS entregas,
       round(sum(inversion_mxn) / nullif(sum(leads), 0))                  AS cpl,
       round(sum(inversion_mxn) / nullif(sum(entregas_acumuladas), 0))    AS cac,
       round(sum(entregas_acumuladas)::numeric / sum(leads), 4)           AS lead_a_entrega
FROM impulso.canales WHERE mes_creacion BETWEEN '2026-05' AND '2026-09'
GROUP BY canal;

------------------------------------------------------------------ CONDUCE
-- Retención a 90 días por firma. Sólo firmas con ≥90 días de observación (firma ≤ 6-ago-2026).
-- Se excluyen bajas por 'Cierre de hub' (Hub Roma, 15-abr): no son decisión del conductor.
CREATE OR REPLACE VIEW conduce.v_retencion90 AS
SELECT c.*,
       CASE WHEN hub LIKE 'Hub Sur%' THEN 'Sur' ELSE 'Resto' END AS zona_hub,
       CASE WHEN distancia_casa_hub_km < 10 THEN '<10 km' ELSE '10+ km' END AS banda_distancia,
       (fecha_baja IS NULL OR fecha_baja > fecha_firma + 90) AS retenido_90d,
       (fecha_baja IS NOT NULL AND fecha_baja - fecha_firma <= 14) AS baja_2_semanas
FROM conduce.conductores c
WHERE fecha_firma <= DATE '2026-08-06' AND coalesce(motivo_baja, '') <> 'Cierre de hub';

-- Cobertura mensual por hub. Excluye la semana de Hub Sur B anterior a su apertura (1-may) — artefacto.
CREATE OR REPLACE VIEW conduce.v_cobertura_mensual AS
SELECT to_char(date_trunc('month', s.semana), 'YYYY-MM') AS mes, s.hub,
       sum(turnos_disponibles) AS disponibles, sum(turnos_cubiertos) AS cubiertos,
       round(sum(turnos_cubiertos)::numeric / nullif(sum(turnos_disponibles), 0), 3) AS cobertura,
       greatest(round(0.92 * sum(turnos_disponibles)) - sum(turnos_cubiertos), 0) AS turnos_bajo_meta
FROM conduce.cobertura_semanal s JOIN conduce.hubs h USING (hub)
WHERE s.semana >= h.fecha_apertura  -- excluye la semana del 27-abr de Sur B (abrió 1-may)
GROUP BY 1, 2;

-- Funnel de reclutamiento por hub: el sur tiene leads; pierde en la asistencia a inducción.
CREATE OR REPLACE VIEW conduce.v_funnel_hub AS
SELECT hub, sum(leads) leads, sum(centro_de_carga) centro_de_carga, sum(revision) revision,
       sum(citados_induccion) citados, sum(asistieron_induccion) asistieron, sum(firmas) firmas,
       round(sum(asistieron_induccion)::numeric / nullif(sum(citados_induccion), 0), 3) AS show_rate,
       round(sum(firmas)::numeric / sum(leads), 3) AS lead_a_firma
FROM conduce.funnel_mensual GROUP BY hub;

------------------------------------------------------------------ WATTS
-- Uso mensual por hub con margen de energía, margen después de fijo, utilización reportada e instalada.
-- Utilización instalada = ocupadas / (conectores instalados × 24 × días): detecta conectores caídos (D-04).
CREATE OR REPLACE VIEW watts.v_hub_mes AS
SELECT m.mes, m.hub_id, h.tipo, h.zona, h.fecha_apertura, h.descuento_promo_agosto,
       (date_part('year', age(to_date(m.mes, 'YYYY-MM') + interval '1 month' - interval '1 day', h.fecha_apertura)) * 12
        + date_part('month', age(to_date(m.mes, 'YYYY-MM') + interval '1 month' - interval '1 day', h.fecha_apertura)))::int AS meses_abierto,
       m.sesiones, m.kwh, m.ingreso_mxn, m.costo_energia_mxn,
       m.ingreso_mxn - m.costo_energia_mxn                                   AS margen_energia,
       m.ingreso_mxn - m.costo_energia_mxn - h.costo_fijo_mensual_mxn        AS margen_tras_fijo,
       round(m.ingreso_mxn / nullif(m.kwh, 0), 2)                            AS precio_efectivo_kwh,
       h.costo_energia_kwh,
       round(m.horas_conector_ocupadas / nullif(m.horas_conector_disponibles, 0), 4) AS utilizacion,
       round(m.horas_conector_ocupadas / (h.conectores * 24 * m.dias_abierto), 4)     AS utilizacion_instalada
FROM watts.hub_mensual m JOIN watts.hubs h USING (hub_id);

-- Propuesta de Marketing: hubs destination con utilización < 10% en oct-2026 y su margen con promo.
-- Supuestos: descuento 25% (punto medio 20–30%) sobre el precio efectivo de oct; volumen ×1.7
-- (alza observada en D-02/D-05, los únicos promo-hubs maduros: ago vs prom. jul–sep).
CREATE OR REPLACE VIEW watts.v_propuesta_q1 AS
SELECT hub_id, meses_abierto, utilizacion, utilizacion_instalada, kwh, precio_efectivo_kwh, costo_energia_kwh,
       margen_energia AS margen_oct,
       round(kwh * 1.7 * (precio_efectivo_kwh * 0.75 - costo_energia_kwh)) AS margen_con_promo,
       round(kwh * 1.7 * (precio_efectivo_kwh * 0.75 - costo_energia_kwh) - margen_energia) AS delta_mensual,
       CASE WHEN precio_efectivo_kwh * 0.75 <= costo_energia_kwh THEN NULL
            ELSE round((precio_efectivo_kwh - costo_energia_kwh) / (precio_efectivo_kwh * 0.75 - costo_energia_kwh), 1) END
         AS multiplicador_breakeven
FROM watts.v_hub_mes
WHERE mes = '2026-10' AND tipo = 'Destination' AND utilizacion < 0.10;
