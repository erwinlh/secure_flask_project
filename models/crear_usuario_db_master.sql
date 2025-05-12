-- Paso 1: Crear el usuario
CREATE USER IF NOT EXISTS 'flask_app_user'@'%' IDENTIFIED BY 'appPassword';

-- Paso 2: Otorgar privilegios al usuario
GRANT SELECT, INSERT, UPDATE, DELETE ON used_db.* TO 'flask_app_user'@'%';

-- Paso 3 (Opcional): Refrescar los privilegios
FLUSH PRIVILEGES;