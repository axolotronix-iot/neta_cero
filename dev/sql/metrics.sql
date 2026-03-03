CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) NOT NULL,
    display_name VARCHAR(150),
    unit VARCHAR(30),
    description TEXT
);