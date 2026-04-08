-- 002_seed_test_users.sql
-- Inserta 3 usuarios de prueba con UUIDs anónimos

INSERT INTO usuarios (uuid_anonimo, nombre_anonimo, semanas_posparto)
VALUES
    ('test-uuid-001', 'Usuaria Alfa', 2),
    ('test-uuid-002', 'Usuaria Beta', 5),
    ('test-uuid-003', 'Usuaria Gamma', 8)
ON CONFLICT (uuid_anonimo) DO NOTHING;
