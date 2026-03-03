CREATE OR REPLACE VIEW v_devices_full AS
SELECT 
    d.id AS device_id,
    d.name AS device_name,
    d.hardware_id,
    o.name AS organization_name,
    o.slug AS org_slug,
    d.is_active,
    -- Formateo de fecha para lectura humana
    d.created_at AT TIME ZONE 'America/Mexico_City' AS registered_at,
    -- Extraer campos específicos del JSONB para verlos como columnas normales
    d.metadata->>'model' AS model,
    d.metadata->>'location' AS location,
    d.metadata->>'fw_version' AS firmware,
    d.metadata AS raw_metadata
FROM devices d
JOIN organizations o ON d.owner_id = o.id;