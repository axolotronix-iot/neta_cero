-- Organizations: Stores the multi-tenant entities that own devices and users
CREATE TABLE organizations (
    -- Unique internal identifier for the organization
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Legal or commercial name of the organization
    name VARCHAR(100) NOT NULL,
    -- URL-friendly identifier for the organization (must be unique)
    slug VARCHAR(50) UNIQUE NOT NULL,
    -- Operational status of the organization
    is_active BOOLEAN DEFAULT TRUE,
    -- Audit timestamp for organization creation
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users: Individuals with access to the platform, tied to an organization
CREATE TABLE users (
    -- Unique internal identifier for the user
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Reference to the organization this user belongs to
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    -- Unique login email address
    email VARCHAR(255) UNIQUE NOT NULL,
    -- Encrypted password storage
    password_hash VARCHAR(255) NOT NULL,
    -- Access level (e.g., 'admin', 'editor', 'viewer')
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    -- Operational status of the user account
    is_active BOOLEAN DEFAULT TRUE,
    -- Audit timestamp for user registration
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Last recorded successful authentication
    last_login TIMESTAMPTZ
);

-- Devices: Physical or logical hardware generating data
CREATE TABLE devices (
    -- Unique internal identifier for the device
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Friendly name for the device in the UI
    name VARCHAR(100) NOT NULL,
    -- Unique physical identifier (MAC address, IMEI, Serial)
    hardware_id VARCHAR(100) UNIQUE NOT NULL,
    -- Reference to the organization that owns this device
    owner_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    -- Connectivity or operational status
    is_active BOOLEAN DEFAULT TRUE,
    -- Audit timestamp for device onboarding
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Audit timestamp for last configuration change
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- Flexible storage for device-specific attributes or firmware info
    metadata JSONB
);

-- Metrics: Catalog of available measurement types
CREATE TABLE metrics (
    -- Unique identifier for the metric type
    id SERIAL PRIMARY KEY,
    -- Unique code for programmatic access (e.g., 'temp_c', 'humidity_pct')
    code VARCHAR(100) UNIQUE NOT NULL,
    -- Human-readable label for dashboards
    display_name VARCHAR(150),
    -- Standard unit symbol (e.g., '°C', '%', 'hPa')
    unit VARCHAR(30),
    -- Detailed explanation of the measurement purpose
    description TEXT
);

-- Telemetry: High-speed ingestion table (No physical FKs for maximum performance)
CREATE TABLE IF NOT EXISTS telemetry (
    -- Unique identifier for the device (Validated at Backend/Cache level)
    device_id UUID NOT NULL,
    -- Reference to the metric type (Validated at Backend/Cache level)
    metric_id INTEGER NOT NULL,
    -- Original timestamp from the device hardware
    ts TIMESTAMPTZ NOT NULL,
    -- Numerical measurement value
    value DOUBLE PRECISION,
    -- Server-side timestamp for data ingestion audit
    ts_ingest TIMESTAMPTZ DEFAULT NOW(),   
    -- Composite PK: Essential for time-series performance and preventing exact duplicates
    PRIMARY KEY (device_id, metric_id, ts)
);
-- Index for efficient data retention management and ingestion auditing
CREATE INDEX idx_telemetry_ingest ON telemetry (ts_ingest);

-- Index for fast user lookup within an organization context
CREATE INDEX idx_users_org ON users (org_id);

-- Index for fast device listing for a specific organization
CREATE INDEX idx_devices_owner ON devices (owner_id);