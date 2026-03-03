SELECT device_name, hardware_id, organization_name, model 
FROM v_devices_full 
WHERE is_active = TRUE;