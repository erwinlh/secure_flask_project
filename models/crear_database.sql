-- database_setup.sql

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS app_db;

-- Usar la base de datos
USE used_db;

-- Crear la tabla de usuarios si no existe (para la primera vez)
-- Si ya tienes la tabla, omite este CREATE TABLE y ve al ALTER TABLE
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    hash VARCHAR(255) NOT NULL, -- Contraseña hasheada
    -- Campos para información personal sensible (cifrados)
    email VARBINARY(255),
    telefono VARBINARY(255),
    rut VARBINARY(255),
    direccion VARBINARY(500),
    nota_secreta VARBINARY(255), -- Campo existente para nota secreta

    -- Campos para hashes de búsqueda (opcional, para búsquedas sin descifrar)
    email_hash VARBINARY(64) UNIQUE, -- Hash SHA256 del email para búsquedas
    rut_hash VARBINARY(64) UNIQUE,   -- Hash SHA256 del RUT para búsquedas

    -- Nivel de usuario (ENUM con 'pending' como opción inicial)
    -- 'pending' será el nivel por defecto para nuevas cuentas.
    nivel ENUM('pending', 'user', 'admin', 'master') NOT NULL DEFAULT 'pending',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ALTER TABLE para añadir o modificar columnas si la tabla ya existe
-- Ejecuta esto si tu tabla `usuarios` ya existe pero no tiene los nuevos campos
-- o si el `nivel` no tiene el ENUM 'pending'.

-- Modificar la columna `nivel` para incluir 'pending' y establecerlo como DEFAULT
-- NOTA: Si ya tienes datos y quieres que los usuarios existentes (sin nivel o con 'user')
-- pasen por el proceso de aprobación, después de este ALTER, necesitarías un
-- UPDATE usuarios SET nivel = 'pending' WHERE nivel = 'user'; (¡Cuidado al usarlo en prod!)
ALTER TABLE usuarios
MODIFY COLUMN nivel ENUM('pending', 'user', 'admin', 'master') NOT NULL DEFAULT 'pending';

-- Añadir las columnas para información personal cifrada si no existen
-- Usar IF NOT EXISTS es una buena práctica aquí.
-- Se añaden AFTER para un orden más lógico, puedes ajustar la posición.
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS email VARBINARY(255) AFTER hash,
ADD COLUMN IF NOT EXISTS telefono VARBINARY(255) AFTER email,
ADD COLUMN IF NOT EXISTS rut VARBINARY(255) AFTER telefono,
ADD COLUMN IF NOT EXISTS direccion VARBINARY(500) AFTER rut,
ADD COLUMN IF NOT EXISTS email_hash VARBINARY(64) UNIQUE AFTER email, -- Para búsquedas
ADD COLUMN IF NOT EXISTS rut_hash VARBINARY(64) UNIQUE AFTER rut;     -- Para búsquedas

-- Asegurarse de que nota_secreta sea VARBINARY si no lo era (o si la tabla se creó sin tipo)
-- Si ya la definiste como VARBINARY(255) no es necesario esto.
ALTER TABLE usuarios
MODIFY COLUMN IF EXISTS nota_secreta VARBINARY(255);

-- Ejemplo para generar el primer usuario master (DESPUÉS de haber corrido el script Python `crear_usuario_master.py`)
-- NOTA: El script crear_usuario_master.py te pedirá credenciales y generará el hash
--       y luego lo insertará directamente en la base de datos con nivel 'master'.
--       No uses este INSERT directamente en producción si no sabes el hash de la contraseña.
-- INSERT INTO usuarios (usuario, hash, nivel, email, telefono, rut, direccion)
-- VALUES ('master_admin', 'EL_HASH_GENERADO_DEL_MASTER_PASSWORD', 'master', NULL, NULL, NULL, NULL);