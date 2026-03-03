-- 1. Insert an Organization
INSERT INTO organizations (name, slug) 
VALUES ('Neta Cero', 'neta-cero');

-- 2. Insert a User (linked to the organization above)
-- Note: Subquery matches the 'neta-cero' slug correctly now
INSERT INTO users (org_id, email, password_hash, role)
VALUES (
    (SELECT id FROM organizations WHERE slug = 'neta-cero'),
    'admin@netacero.com',
    '12345', 
    'admin'
);

-- 3. Insert the Initial Metrics Catalog
INSERT INTO metrics (code, display_name, unit, description)
VALUES 
    ('temp_c', 'Ambient Temperature', '°C', 'Air temperature measured in Celsius'),
    ('humi_pct', 'Relative Humidity', '%', 'Percentage of water vapor in the air'),
    ('batt_v', 'Battery Voltage', 'V', 'Device internal battery level'),
    ('soil_moist', 'Soil Moisture', 'cb', 'Soil tension/moisture level'),
    ('tank_low_bool', 'Tank Low Level Alert', 'bool', '0: OK, 1: Critical Low Water'),
    ('tank_full_bool', 'Tank Full Status', 'bool', '0: Filling/Normal, 1: Tank Full'),
    ('flow_rate', 'Water Consumption Flow', 'L/min', 'Real-time water usage flow rate');

-- 4. Insert Test Devices
-- Both sensors linked to 'neta-cero' organization
INSERT INTO devices (name, hardware_id, owner_id, metadata)
VALUES 
    (
        'Wash Sensor 01', 
        '10:91:A8:1E:77:9C', 
        (SELECT id FROM organizations WHERE slug = 'neta-cero'),
        '{"model": "ESP32C3-NC1000", "fw_version": "1.0.0", "location": "Sector A"}'
    ),
    (
        'Wash Sensor 02', 
        '2C:CF:67:CB:2D:8A', 
        (SELECT id FROM organizations WHERE slug = 'neta-cero'),
        '{"model": "PICO2W-NC1000", "fw_version": "1.0.0", "location": "Sector B"}'
    );