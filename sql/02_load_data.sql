-- Vemo · Carga de los CSV exportados de los Excel (tools/data_prep/xlsx_to_csv.py)
-- Idempotente: vacía y recarga. Los CSV se montan en /data dentro del contenedor.

-- ---------- impulso ----------
TRUNCATE impulso.leeme RESTART IDENTITY;
COPY impulso.leeme (texto) FROM '/data/impulso/LEEME.csv' WITH (FORMAT csv, HEADER false, NULL '');
TRUNCATE impulso.canales;
COPY impulso.canales (mes_creacion, canal, inversion_mxn, leads, calificados, entregas_acumuladas)
    FROM '/data/impulso/canales.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE impulso.cohortes;
COPY impulso.cohortes (mes_creacion, leads, contactados, enviados_a_analisis, calificados, visitas_aprobadas, perdidos_en_visita_por_deposito, perdidos_en_visita_otros_motivos, entregas_acumuladas, dias_mediana_lead_a_entrega, leads_aun_en_proceso)
    FROM '/data/impulso/cohortes.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE impulso.funnel_mensual;
COPY impulso.funnel_mensual (mes, leads_creados, contactados, contactados_por_agente_ia, enviados_a_analisis, rechazados_buro, rechazados_riesgo, calificados, dias_mediana_analisis, visitas_aprobadas, entregas)
    FROM '/data/impulso/funnel_mensual.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE impulso.supuestos;
COPY impulso.supuestos (supuesto, valor, nota)
    FROM '/data/impulso/supuestos.csv' WITH (FORMAT csv, HEADER true, NULL '');

-- ---------- conduce ----------
TRUNCATE conduce.leeme RESTART IDENTITY;
COPY conduce.leeme (texto) FROM '/data/conduce/LEEME.csv' WITH (FORMAT csv, HEADER false, NULL '');
TRUNCATE conduce.cobertura_semanal;
COPY conduce.cobertura_semanal (semana, hub, turno, turnos_disponibles, turnos_cubiertos)
    FROM '/data/conduce/cobertura_semanal.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE conduce.conductores;
COPY conduce.conductores (conductor_id, persona_id, fecha_firma, hub, turno, canal, distancia_casa_hub_km, horas_semanales_prom, bono_semanal_prom_mxn, fecha_baja, motivo_baja)
    FROM '/data/conduce/conductores.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE conduce.funnel_mensual;
COPY conduce.funnel_mensual (mes, hub, turno, leads, centro_de_carga, revision, citados_induccion, asistieron_induccion, firmas)
    FROM '/data/conduce/funnel_mensual.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE conduce.hubs;
COPY conduce.hubs (hub, zona, autos, fecha_apertura, fecha_cierre, nota)
    FROM '/data/conduce/hubs.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE conduce.inversion_mensual;
COPY conduce.inversion_mensual (mes, canal, inversion_mxn)
    FROM '/data/conduce/inversion_mensual.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE conduce.supuestos;
COPY conduce.supuestos (supuesto, valor, nota)
    FROM '/data/conduce/supuestos.csv' WITH (FORMAT csv, HEADER true, NULL '');

-- ---------- watts ----------
TRUNCATE watts.leeme RESTART IDENTITY;
COPY watts.leeme (texto) FROM '/data/watts/LEEME.csv' WITH (FORMAT csv, HEADER false, NULL '');
TRUNCATE watts.hub_mensual;
COPY watts.hub_mensual (mes, hub_id, dias_abierto, conectores_operativos_prom, horas_conector_disponibles, sesiones, kwh, horas_conector_ocupadas, ingreso_mxn, costo_energia_mxn)
    FROM '/data/watts/hub_mensual.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE watts.hubs;
COPY watts.hubs (hub_id, tipo, zona, fecha_apertura, conectores, potencia_kw, precio_publico_kwh, costo_energia_kwh, costo_fijo_mensual_mxn, descuento_promo_agosto)
    FROM '/data/watts/hubs.csv' WITH (FORMAT csv, HEADER true, NULL '');
TRUNCATE watts.supuestos;
COPY watts.supuestos (supuesto, valor, nota)
    FROM '/data/watts/supuestos.csv' WITH (FORMAT csv, HEADER true, NULL '');
