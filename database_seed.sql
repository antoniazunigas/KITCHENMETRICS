-- =========================================================
-- KitchenMetrics - database_seed.sql
-- =========================================================

-- =========================================================
-- 1. LIMPIEZA TOTAL
-- =========================================================
DELETE FROM merma_preparada;
DELETE FROM merma_ingrediente;
DELETE FROM consumo;
DELETE FROM reserva;
DELETE FROM jornada_cocina;
DELETE FROM menu_detalle;
DELETE FROM receta;
DELETE FROM lote_ingrediente;
DELETE FROM menu_dia;
DELETE FROM plato;
DELETE FROM ingrediente;
DELETE FROM usuario;
DELETE FROM rol;
DELETE FROM reporte_operativo;

-- =========================================================
-- 2. ROLES
-- =========================================================
INSERT INTO rol (id_rol, nombre) VALUES
(1, 'admin'),
(2, 'cocina'),
(3, 'funcionario'),
(4, 'jefe_cocina');

-- =========================================================
-- 3. USUARIOS BASE
-- =========================================================
INSERT INTO usuario
(id_usuario, id_rol, rut, nombre, apellido, email, contrasena, faltas_acumuladas, estado) VALUES
(1, 1, '184562346', 'Ana', 'Rojas', 'ana.rojas@hospital.cl', '1234', 0, 'activo'),
(2, 2, '227749806', 'Luis', 'Pérez', 'luis.perez@hospital.cl', '1234', 0, 'activo'),
(3, 3, '205577648', 'Marta', 'Gómez', 'marta.gomez@hospital.cl', '1234', 0, 'activo'),
(4, 4, '89905467',  'Carlos', 'Díaz', 'carlos.diaz@hospital.cl', '1234', 0, 'activo'),
(5, 2, '123360094', 'Sofía', 'Mora', 'sofia.mora@hospital.cl', '1234', 0, 'activo'),
(6, 1, '186634568', 'Pedro', 'Luna', 'pedro.luna@hospital.cl', '1234', 0, 'activo'),
(7, 3, '130078975', 'Elena', 'Vega', 'elena.vega@hospital.cl', '1234', 0, 'activo'),
(8, 3, '187746239', 'Diego', 'Fuentes', 'diego.fuentes@hospital.cl', '1234', 0, 'activo'),
(9, 3, '150079984', 'Camila', 'Reyes', 'camila.reyes@hospital.cl', '1234', 0, 'activo'),
(10, 3, '130963457', 'Jorge', 'Navarro', 'jorge.navarro@hospital.cl', '1234', 0, 'activo');

-- Usuarios dummy para reservas y pruebas
INSERT INTO usuario
(id_usuario, id_rol, rut, nombre, apellido, email, contrasena, faltas_acumuladas, estado)
SELECT
    gs,
    3,
    '1000' || gs,
    'User' || gs,
    'Test',
    'user' || gs || '@mail.com',
    '1234',
    faltas.faltas_acumuladas,
    CASE WHEN faltas.faltas_acumuladas >= 3 THEN 'bloqueado' ELSE 'activo' END
FROM (
    SELECT gs, floor(random() * 5)::int AS faltas_acumuladas
    FROM generate_series(11, 150) AS gs
) AS faltas
ON CONFLICT (id_usuario) DO NOTHING;

UPDATE usuario
SET estado = CASE WHEN faltas_acumuladas >= 3 THEN 'bloqueado' ELSE 'activo' END;

-- =========================================================
-- 4. INGREDIENTES
-- =========================================================
INSERT INTO ingrediente (id_ingrediente, nombre, unidad_medida) VALUES
(1,  'Arroz', 'kg'),
(2,  'Pollo', 'kg'),
(3,  'Carne', 'kg'),
(4,  'Tomate', 'kg'),
(5,  'Lechuga', 'unidad'),
(6,  'Papa', 'kg'),
(7,  'Aceite', 'lt'),
(8,  'Sal', 'gr'),
(9,  'Harina', 'kg'),
(10, 'Azucar', 'gr'),
(11, 'Tallarines', 'kg'),
(12, 'Lentejas', 'kg'),
(13, 'Leche', 'lt'),
(14, 'Queso', 'kg');

-- =========================================================
-- 5. PLATOS
-- =========================================================
INSERT INTO plato (id_plato, nombre, tipo_plato, tipo_dieta) VALUES
(1, 'Ensalada Mixta', 'entrada', 'Normal'),
(2, 'Pollo con Arroz', 'fondo', 'Normal'),
(3, 'Carne con Papas', 'fondo', 'Normal'),
(4, 'Postre del Dia', 'postre', 'Normal'),
(5, 'Sopa de Verduras', 'entrada', 'Normal'),
(6, 'Lentejas Guisadas', 'fondo', 'Vegano'),
(7, 'Pasta Vegetariana', 'fondo', 'Vegano'),
(8, 'Fruta', 'postre', 'Normal'),
(9, 'Sopa de Pollo', 'entrada', 'Normal'),
(10, 'Puré de Papas', 'fondo', 'Normal'),
(11, 'Tallarines con Salsa', 'fondo', 'Normal'),
(12, 'Leche con Galletas', 'postre', 'Normal'),
(13, 'Ensalada de Lentejas', 'entrada', 'Vegano'),
(14, 'Tortilla de Verduras', 'fondo', 'Vegetariano'),
(15, 'Queso con Tomate', 'entrada', 'Vegetariano'),
(16, 'Pasta con Queso', 'fondo', 'Vegetariano'),
(17, 'Fruta con Queso', 'postre', 'Vegetariano'),
(18, 'Sopa de Tomate', 'entrada', 'Vegano'),
(19, 'Carne con Tallarines', 'fondo', 'Normal'),
(20, 'Puré de Lentejas', 'fondo', 'Vegano'),
(21, 'Ensalada César', 'entrada', 'Normal'),
(22, 'Risotto de Champiñones', 'fondo', 'Vegetariano'),
(23, 'Hamburguesa Vegana', 'fondo', 'Vegano'),
(24, 'Helado de Vainilla', 'postre', 'Normal'),
(25, 'Gazpacho', 'entrada', 'Vegano'),
(26, 'Lasagna de Carne', 'fondo', 'Normal'),
(27, 'Lasagna Vegetariana', 'fondo', 'Vegetariano'),
(28, 'Brownie de Chocolate', 'postre', 'Vegetariano'),
(29, 'Crema de Espinacas', 'entrada', 'Vegetariano'),
(30, 'Filete de Pescado', 'fondo', 'Normal'),
(31, 'Pizza Margarita', 'fondo', 'Vegetariano'),
(32, 'Pizza Vegana', 'fondo', 'Vegano'),
(33, 'Tarta de Manzana', 'postre', 'Normal'),
(34, 'Ensalada de Garbanzos', 'entrada', 'Vegano'),
(35, 'Arroz con Mariscos', 'fondo', 'Normal'),
(36, 'Quiche de Verduras', 'fondo', 'Vegetariano'),
(37, 'Yogurt con Frutas', 'postre', 'Vegetariano'),
(38, 'Sopa de Calabaza', 'entrada', 'Vegano'),
(39, 'Estofado de Ternera', 'fondo', 'Normal'),
(40, 'Mousse de Chocolate', 'postre', 'Vegetariano');


-- =========================================================
-- 6. RECETAS
-- =========================================================
INSERT INTO receta (id_plato, id_ingrediente, cantidad_por_porcion) VALUES
(1,  5, 0.500),
(1,  4, 0.100),
(1,  7, 0.015),

(2,  2, 0.250),
(2,  1, 0.100),
(2,  7, 0.010),

(3,  3, 0.200),
(3,  6, 0.300),
(3,  7, 0.010),

(4, 10, 0.050),

(6, 12, 0.200),
(6,  8, 0.005),

(7, 11, 0.150),
(7,  4, 0.100),
(7,  7, 0.010);

-- =========================================================
-- 7. MENÚS (60 días)
-- 30 días hacia atrás + hoy + 29 días futuro
-- =========================================================
INSERT INTO menu_dia (id_menu, fecha, estado)
SELECT
    i,
    (CURRENT_DATE - INTERVAL '30 days' + ((i - 1) || ' day')::interval)::date,
    'activo'
FROM generate_series(1, 60) AS i;

-- =========================================================
-- 8. DETALLE MENÚ
-- 1 entrada, 3 fondos posibles, 1 postre
-- =========================================================
INSERT INTO menu_detalle (id_menu, id_plato, orden)
SELECT id_menu, 1, 1 FROM menu_dia;

INSERT INTO menu_detalle (id_menu, id_plato, orden)
SELECT id_menu, CASE WHEN id_menu % 2 = 0 THEN 2 ELSE 3 END, 2
FROM menu_dia;

INSERT INTO menu_detalle (id_menu, id_plato, orden)
SELECT id_menu, CASE WHEN id_menu % 2 = 0 THEN 3 ELSE 2 END, 3
FROM menu_dia;

INSERT INTO menu_detalle (id_menu, id_plato, orden)
SELECT id_menu, CASE WHEN id_menu % 2 = 0 THEN 6 ELSE 7 END, 4
FROM menu_dia;

INSERT INTO menu_detalle (id_menu, id_plato, orden)
SELECT id_menu, 4, 5
FROM menu_dia;

-- =========================================================
-- 9. JORNADAS
-- =========================================================
INSERT INTO jornada_cocina
(id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
SELECT id_menu, id_menu, 150, 140, 10
FROM menu_dia;

-- =========================================================
-- 10. LOTES
-- =========================================================
INSERT INTO lote_ingrediente
(id_lote, id_ingrediente, fecha_ingreso, fecha_vencimiento, cantidad_inicial, cantidad_disponible, costo_unitario)
VALUES
(1, 1, CURRENT_DATE - INTERVAL '4 days', CURRENT_DATE + INTERVAL '26 days', 50.000, 40.000, 1500.00),
(2, 2, CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '7 days',  40.000, 25.000, 9000.00),
(3, 3, CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE + INTERVAL '8 days',  30.000, 18.000, 8500.00),
(4, 6, CURRENT_DATE - INTERVAL '1 day',  CURRENT_DATE + INTERVAL '15 days', 60.000, 45.000, 800.00);

-- =========================================================
-- 11. MERMAS BASE
-- =========================================================
INSERT INTO merma_ingrediente
(id_merma_ing, id_lote, fecha, cantidad, costo_perdido, motivo) VALUES
(1, 1, CURRENT_DATE - INTERVAL '1 day', 0.300, 450.00,  'vencimiento'),
(2, 2, CURRENT_DATE - INTERVAL '1 day', 0.200, 1800.00, 'deterioro'),
(3, 4, CURRENT_DATE - INTERVAL '1 day', 0.100, 80.00,   'sobrante');

INSERT INTO merma_preparada
(id_merma_prep, id_jornada, fecha, cantidad_raciones, costo_perdido, motivo) VALUES
(1, 1, CURRENT_DATE - INTERVAL '1 day', 10, 15000.00, 'sobrante');

-- =========================================================
-- 12. RESERVAS + CONSUMO (HISTÓRICO + ACTUAL)
-- =========================================================
DO $$
DECLARE
    u INT;
    j INT;
    v_reserva INT := 1;
    v_consumo INT := 1;
    v_fecha_menu DATE;
    v_estado TEXT;
    v_fecha_reserva TIMESTAMP;
    v_fecha_consumo TIMESTAMP;
    v_id_plato_fondo INT;

    v_total_usuarios INT := 50;
    v_faltas_objetivo INT;
    v_contador INT;
BEGIN

    FOR j IN 1..60 LOOP

        v_fecha_menu := (CURRENT_DATE - INTERVAL '30 days' + ((j - 1) || ' day')::interval)::date;

        v_contador := 0;
        v_faltas_objetivo := CEIL(v_total_usuarios * (0.04 + random() * 0.04));

        FOR u IN 11..(10 + v_total_usuarios) LOOP

            -- =========================
            -- PASADO (histórico real)
            -- =========================
            IF v_fecha_menu < CURRENT_DATE THEN

                IF v_contador < v_faltas_objetivo THEN
                    v_estado := 'no_retirada';
                    v_contador := v_contador + 1;
                ELSE
                    v_estado := 'consumida';
                END IF;

                v_fecha_reserva := (v_fecha_menu + TIME '08:00:00');
                v_fecha_consumo := (v_fecha_menu + TIME '12:30:00');

            -- =========================
            -- HOY
            -- =========================
            ELSIF v_fecha_menu = CURRENT_DATE THEN

                IF u <= 40 THEN
                    v_estado := 'consumida';
                ELSE
                    v_estado := 'confirmada';
                END IF;

                v_fecha_reserva := (CURRENT_DATE + TIME '08:00:00');
                v_fecha_consumo := (CURRENT_DATE + TIME '12:30:00');

            -- =========================
            -- FUTURO (intacto)
            -- =========================
            ELSE
                v_estado := 'confirmada';
                v_fecha_reserva := (CURRENT_DATE + TIME '08:00:00');
                v_fecha_consumo := NULL;
            END IF;

            -- Asignar un fondo aleatorio de los disponibles para este menú
            SELECT md.id_plato INTO v_id_plato_fondo
            FROM menu_detalle md
            WHERE md.id_menu = j AND md.orden IN (2, 3, 4)
            ORDER BY random() LIMIT 1;

            INSERT INTO reserva
            (id_reserva, id_usuario, id_jornada, fecha_reserva, estado, id_plato_fondo)
            VALUES
            (v_reserva, u, j, v_fecha_reserva, v_estado, v_id_plato_fondo);

            IF v_estado = 'consumida' THEN
                INSERT INTO consumo
                (id_consumo, id_reserva, id_jornada, fecha_consumo, estado)
                VALUES
                (v_consumo, v_reserva, j, v_fecha_consumo, 'registrado');

                v_consumo := v_consumo + 1;
            END IF;

            v_reserva := v_reserva + 1;

        END LOOP;
    END LOOP;

END $$;

-- =========================================================
-- 13. AJUSTE DE SECUENCIAS
-- =========================================================
SELECT setval(pg_get_serial_sequence('rol','id_rol'),
              COALESCE((SELECT MAX(id_rol) FROM rol), 1), true);

SELECT setval(pg_get_serial_sequence('usuario','id_usuario'),
              COALESCE((SELECT MAX(id_usuario) FROM usuario), 1), true);

SELECT setval(pg_get_serial_sequence('ingrediente','id_ingrediente'),
              COALESCE((SELECT MAX(id_ingrediente) FROM ingrediente), 1), true);

SELECT setval(pg_get_serial_sequence('plato','id_plato'),
              COALESCE((SELECT MAX(id_plato) FROM plato), 1), true);

SELECT setval(pg_get_serial_sequence('menu_dia','id_menu'),
              COALESCE((SELECT MAX(id_menu) FROM menu_dia), 1), true);

SELECT setval(pg_get_serial_sequence('menu_detalle','id_menu_detalle'),
              COALESCE((SELECT MAX(id_menu_detalle) FROM menu_detalle), 1), true);

SELECT setval(pg_get_serial_sequence('jornada_cocina','id_jornada'),
              COALESCE((SELECT MAX(id_jornada) FROM jornada_cocina), 1), true);

SELECT setval(pg_get_serial_sequence('lote_ingrediente','id_lote'),
              COALESCE((SELECT MAX(id_lote) FROM lote_ingrediente), 1), true);

SELECT setval(pg_get_serial_sequence('receta','id_receta'),
              COALESCE((SELECT MAX(id_receta) FROM receta), 1), true);

SELECT setval(pg_get_serial_sequence('reserva','id_reserva'),
              COALESCE((SELECT MAX(id_reserva) FROM reserva), 1), true);

SELECT setval(pg_get_serial_sequence('consumo','id_consumo'),
              COALESCE((SELECT MAX(id_consumo) FROM consumo), 1), true);

SELECT setval(pg_get_serial_sequence('merma_ingrediente','id_merma_ing'),
              COALESCE((SELECT MAX(id_merma_ing) FROM merma_ingrediente), 1), true);

SELECT setval(pg_get_serial_sequence('merma_preparada','id_merma_prep'),
              COALESCE((SELECT MAX(id_merma_prep) FROM merma_preparada), 1), true);


-- =========================================================
-- 14. TABLA DE REPORTES OPERATIVOS
-- =========================================================
CREATE TABLE IF NOT EXISTS reporte_operativo (
    id_reporte SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo_reporte VARCHAR(20) NOT NULL,
    total_reservas INT NOT NULL DEFAULT 0,
    total_consumidas INT NOT NULL DEFAULT 0,
    total_no_retiradas INT NOT NULL DEFAULT 0,
    total_canceladas INT NOT NULL DEFAULT 0,
    tasa_faltas NUMERIC(5,2) NOT NULL DEFAULT 0,
    total_ingredientes_lote INT NOT NULL DEFAULT 0,
    total_stock_disponible NUMERIC(12,3) NOT NULL DEFAULT 0,
    total_merma_ingrediente NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_merma_preparada NUMERIC(12,2) NOT NULL DEFAULT 0,
    costo_total_perdido NUMERIC(12,2) NOT NULL DEFAULT 0,
    actualizado_en TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (fecha, tipo_reporte)
);

-- =========================================================
-- 15. FUNCIÓN DE REGENERACIÓN DE REPORTES
-- =========================================================
CREATE OR REPLACE FUNCTION fn_recalcular_reportes_operativos(p_fecha DATE)
RETURNS VOID AS $$
DECLARE
    v_total_reservas INT := 0;
    v_total_consumidas INT := 0;
    v_total_no_retiradas INT := 0;
    v_total_canceladas INT := 0;
    v_tasa_faltas NUMERIC(5,2) := 0;

    v_total_ingredientes_lote INT := 0;
    v_total_stock_disponible NUMERIC(12,3) := 0;

    v_total_merma_ing NUMERIC(12,2) := 0;
    v_total_merma_prep NUMERIC(12,2) := 0;
    v_costo_total NUMERIC(12,2) := 0;
BEGIN
    -- Reservas / consumo / faltas
    SELECT
        COUNT(*),
        COUNT(*) FILTER (WHERE estado = 'consumida'),
        COUNT(*) FILTER (WHERE estado = 'no_retirada'),
        COUNT(*) FILTER (WHERE estado = 'cancelada')
    INTO
        v_total_reservas,
        v_total_consumidas,
        v_total_no_retiradas,
        v_total_canceladas
    FROM reserva
    WHERE fecha_reserva::DATE = p_fecha;

    IF v_total_reservas > 0 THEN
        v_tasa_faltas := ROUND((v_total_no_retiradas::NUMERIC * 100) / v_total_reservas, 2);
    END IF;

    -- Inventario
    SELECT
        COUNT(*),
        COALESCE(SUM(cantidad_disponible), 0)
    INTO
        v_total_ingredientes_lote,
        v_total_stock_disponible
    FROM lote_ingrediente;

    -- Mermas
    SELECT COALESCE(SUM(costo_perdido), 0)
    INTO v_total_merma_ing
    FROM merma_ingrediente
    WHERE fecha = p_fecha;

    SELECT COALESCE(SUM(costo_perdido), 0)
    INTO v_total_merma_prep
    FROM merma_preparada
    WHERE fecha = p_fecha;

    v_costo_total := v_total_merma_ing + v_total_merma_prep;

    -- Reporte general
    INSERT INTO reporte_operativo (
        fecha, tipo_reporte,
        total_reservas, total_consumidas, total_no_retiradas, total_canceladas,
        tasa_faltas,
        total_ingredientes_lote, total_stock_disponible,
        total_merma_ingrediente, total_merma_preparada, costo_total_perdido,
        actualizado_en
    )
    VALUES (
        p_fecha, 'general',
        v_total_reservas, v_total_consumidas, v_total_no_retiradas, v_total_canceladas,
        v_tasa_faltas,
        v_total_ingredientes_lote, v_total_stock_disponible,
        v_total_merma_ing, v_total_merma_prep, v_costo_total,
        NOW()
    )
    ON CONFLICT (fecha, tipo_reporte) DO UPDATE SET
        total_reservas = EXCLUDED.total_reservas,
        total_consumidas = EXCLUDED.total_consumidas,
        total_no_retiradas = EXCLUDED.total_no_retiradas,
        total_canceladas = EXCLUDED.total_canceladas,
        tasa_faltas = EXCLUDED.tasa_faltas,
        total_ingredientes_lote = EXCLUDED.total_ingredientes_lote,
        total_stock_disponible = EXCLUDED.total_stock_disponible,
        total_merma_ingrediente = EXCLUDED.total_merma_ingrediente,
        total_merma_preparada = EXCLUDED.total_merma_preparada,
        costo_total_perdido = EXCLUDED.costo_total_perdido,
        actualizado_en = NOW();

    -- Reporte inventario
    INSERT INTO reporte_operativo (
        fecha, tipo_reporte,
        total_ingredientes_lote, total_stock_disponible,
        actualizado_en
    )
    VALUES (
        p_fecha, 'inventario',
        v_total_ingredientes_lote, v_total_stock_disponible,
        NOW()
    )
    ON CONFLICT (fecha, tipo_reporte) DO UPDATE SET
        total_ingredientes_lote = EXCLUDED.total_ingredientes_lote,
        total_stock_disponible = EXCLUDED.total_stock_disponible,
        actualizado_en = NOW();

    -- Reporte mermas
    INSERT INTO reporte_operativo (
        fecha, tipo_reporte,
        total_merma_ingrediente, total_merma_preparada, costo_total_perdido,
        actualizado_en
    )
    VALUES (
        p_fecha, 'mermas',
        v_total_merma_ing, v_total_merma_prep, v_costo_total,
        NOW()
    )
    ON CONFLICT (fecha, tipo_reporte) DO UPDATE SET
        total_merma_ingrediente = EXCLUDED.total_merma_ingrediente,
        total_merma_preparada = EXCLUDED.total_merma_preparada,
        costo_total_perdido = EXCLUDED.costo_total_perdido,
        actualizado_en = NOW();
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- 16. FUNCIÓN TRIGGER PARA REPORTE
-- =========================================================
CREATE OR REPLACE FUNCTION fn_trigger_reportes_operativos()
RETURNS TRIGGER AS $$
DECLARE
    v_fecha DATE;
BEGIN
    IF TG_TABLE_NAME = 'reserva' THEN
        v_fecha := COALESCE(NEW.fecha_reserva, OLD.fecha_reserva)::DATE;

    ELSIF TG_TABLE_NAME = 'consumo' THEN
        v_fecha := COALESCE(NEW.fecha_consumo, OLD.fecha_consumo)::DATE;

    ELSIF TG_TABLE_NAME = 'merma_ingrediente' THEN
        v_fecha := COALESCE(NEW.fecha, OLD.fecha);

    ELSIF TG_TABLE_NAME = 'merma_preparada' THEN
        v_fecha := COALESCE(NEW.fecha, OLD.fecha);

    ELSIF TG_TABLE_NAME = 'lote_ingrediente' THEN
        -- No hay fecha directa de reporte; se usa el día actual
        v_fecha := CURRENT_DATE;
    END IF;

    PERFORM fn_recalcular_reportes_operativos(v_fecha);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- 17. TRIGGERS SOBRE TABLAS FUENTE
-- =========================================================
DROP TRIGGER IF EXISTS trg_reportes_reserva ON reserva;
CREATE TRIGGER trg_reportes_reserva
AFTER INSERT OR UPDATE OR DELETE ON reserva
FOR EACH ROW EXECUTE FUNCTION fn_trigger_reportes_operativos();

DROP TRIGGER IF EXISTS trg_reportes_consumo ON consumo;
CREATE TRIGGER trg_reportes_consumo
AFTER INSERT OR UPDATE OR DELETE ON consumo
FOR EACH ROW EXECUTE FUNCTION fn_trigger_reportes_operativos();

DROP TRIGGER IF EXISTS trg_reportes_merma_ingrediente ON merma_ingrediente;
CREATE TRIGGER trg_reportes_merma_ingrediente
AFTER INSERT OR UPDATE OR DELETE ON merma_ingrediente
FOR EACH ROW EXECUTE FUNCTION fn_trigger_reportes_operativos();

DROP TRIGGER IF EXISTS trg_reportes_merma_preparada ON merma_preparada;
CREATE TRIGGER trg_reportes_merma_preparada
AFTER INSERT OR UPDATE OR DELETE ON merma_preparada
FOR EACH ROW EXECUTE FUNCTION fn_trigger_reportes_operativos();

DROP TRIGGER IF EXISTS trg_reportes_lote_ingrediente ON lote_ingrediente;
CREATE TRIGGER trg_reportes_lote_ingrediente
AFTER INSERT OR UPDATE OR DELETE ON lote_ingrediente
FOR EACH ROW EXECUTE FUNCTION fn_trigger_reportes_operativos();

-- =========================================================
-- 18. POBLAR REPORTES INICIALES
-- =========================================================
DO $$
DECLARE f DATE;
BEGIN
    FOR f IN
        SELECT DISTINCT fecha_reserva::DATE FROM reserva
        UNION
        SELECT DISTINCT fecha_consumo::DATE FROM consumo
        UNION
        SELECT DISTINCT fecha FROM merma_ingrediente
        UNION
        SELECT DISTINCT fecha FROM merma_preparada
        UNION
        SELECT CURRENT_DATE
    LOOP
        PERFORM fn_recalcular_reportes_operativos(f);
    END LOOP;
END $$;

-- =========================================================
-- 19. TABLA DE REPORTES DE MERMAS VS CONSUMO
-- =========================================================
CREATE TABLE IF NOT EXISTS reporte_mermas_vs_consumo_mensual(
    id_reporte_mensual SERIAL PRIMARY KEY,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    total_reservas INT NOT NULL DEFAULT 0,
    total_consumidas INT NOT NULL DEFAULT 0,
    total_no_retiradas INT NOT NULL DEFAULT 0,
    tasa_faltas NUMERIC(5,2) NOT NULL DEFAULT 0,
    total_merma_ingrediente NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_merma_preparada NUMERIC(12,2) NOT NULL DEFAULT 0,
    costo_total_perdido NUMERIC(12,2) NOT NULL DEFAULT 0,
    ratio_merma_consumo NUMERIC(12,4) NOT NULL DEFAULT 0,
    observacion TEXT,
    generado_en TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(fecha_inicio,fecha_fin)
);

-- =========================================================
-- 20. PROCEDIMIENTO PARA GENERAR REPORTE MENSUAL DE MERMAS VS CONSUMO
-- =========================================================
CREATE OR REPLACE PROCEDURE sp_generar_reporte_mermas_vs_consumo_ultimo_mes()
LANGUAGE plpgsql AS $$
DECLARE
    v_fecha_fin DATE := CURRENT_DATE - 1;
    v_fecha_inicio DATE := (CURRENT_DATE - INTERVAL '1 month')::DATE;
    v_total_reservas INT := 0;
    v_total_consumidas INT := 0;
    v_total_no_retiradas INT := 0;
    v_tasa_faltas NUMERIC(5,2) := 0;
    v_total_merma_ing NUMERIC(12,2) := 0;
    v_total_merma_prep NUMERIC(12,2) := 0;
    v_costo_total NUMERIC(12,2) := 0;
    v_ratio_merma_consumo NUMERIC(12,4) := 0;
    v_observacion TEXT;
BEGIN
    SELECT COUNT(*),
           COUNT(*) FILTER(WHERE estado='consumida'),
           COUNT(*) FILTER(WHERE estado='no_retirada')
    INTO v_total_reservas,v_total_consumidas,v_total_no_retiradas
    FROM reserva
    WHERE fecha_reserva::DATE BETWEEN v_fecha_inicio AND v_fecha_fin;

    IF v_total_reservas>0 THEN
        v_tasa_faltas := ROUND((v_total_no_retiradas::NUMERIC*100)/v_total_reservas,2);
    END IF;

    SELECT COALESCE(SUM(costo_perdido),0)
    INTO v_total_merma_ing
    FROM merma_ingrediente
    WHERE fecha BETWEEN v_fecha_inicio AND v_fecha_fin;

    SELECT COALESCE(SUM(costo_perdido),0)
    INTO v_total_merma_prep
    FROM merma_preparada
    WHERE fecha BETWEEN v_fecha_inicio AND v_fecha_fin;

    v_costo_total := v_total_merma_ing+v_total_merma_prep;

    IF v_total_consumidas>0 THEN
        v_ratio_merma_consumo := ROUND(v_costo_total/v_total_consumidas,4);
    END IF;

    IF v_tasa_faltas<=8 AND v_costo_total>0 THEN
        v_observacion := 'Desempeño aceptable, pero aún existe pérdida recuperable en mermas.';
    ELSIF v_tasa_faltas>8 THEN
        v_observacion := 'Alta tasa de inasistencia. Revisar bloqueos, reservas y control de retiro.';
    ELSE
        v_observacion := 'Operación controlada con bajo nivel de faltas.';
    END IF;

    INSERT INTO reporte_mermas_vs_consumo_mensual(
        fecha_inicio,fecha_fin,total_reservas,total_consumidas,total_no_retiradas,
        tasa_faltas,total_merma_ingrediente,total_merma_preparada,costo_total_perdido,
        ratio_merma_consumo,observacion,generado_en
    ) VALUES(
        v_fecha_inicio,v_fecha_fin,v_total_reservas,v_total_consumidas,v_total_no_retiradas,
        v_tasa_faltas,v_total_merma_ing,v_total_merma_prep,v_costo_total,
        v_ratio_merma_consumo,v_observacion,NOW()
    )
    ON CONFLICT(fecha_inicio,fecha_fin) DO UPDATE SET
        total_reservas=EXCLUDED.total_reservas,
        total_consumidas=EXCLUDED.total_consumidas,
        total_no_retiradas=EXCLUDED.total_no_retiradas,
        tasa_faltas=EXCLUDED.tasa_faltas,
        total_merma_ingrediente=EXCLUDED.total_merma_ingrediente,
        total_merma_preparada=EXCLUDED.total_merma_preparada,
        costo_total_perdido=EXCLUDED.costo_total_perdido,
        ratio_merma_consumo=EXCLUDED.ratio_merma_consumo,
        observacion=EXCLUDED.observacion,
        generado_en=NOW();
END;
$$;

-- =========================================================
-- 21. EJECUTAR PROCEDIMIENTO PARA POBLAR REPORTE INICIAL
-- =========================================================
CALL sp_generar_reporte_mermas_vs_consumo_ultimo_mes();


-- =========================================================
--  22. LIMPIEZA DE RESERVAS FUTURAS
-- =========================================================
BEGIN;

-- Restaurar cupos antes de borrar reservas futuras (incluye mañana)
UPDATE jornada_cocina j
SET raciones_disponibles = j.raciones_disponibles + sub.total_reservas
FROM (
    SELECT r.id_jornada, COUNT(*) AS total_reservas
    FROM reserva r
    JOIN jornada_cocina j2 ON j2.id_jornada = r.id_jornada
    JOIN menu_dia m ON m.id_menu = j2.id_menu
    WHERE m.fecha >= CURRENT_DATE + INTERVAL '1 day'
    GROUP BY r.id_jornada
) sub
WHERE j.id_jornada = sub.id_jornada;

-- Borrar consumos futuros
DELETE FROM consumo
WHERE id_reserva IN (
    SELECT r.id_reserva
    FROM reserva r
    JOIN jornada_cocina j ON j.id_jornada = r.id_jornada
    JOIN menu_dia m ON m.id_menu = j.id_menu
    WHERE m.fecha >= CURRENT_DATE + INTERVAL '1 day'
);

-- Borrar reservas futuras (mañana y siguientes)
DELETE FROM reserva
WHERE id_reserva IN (
    SELECT r.id_reserva
    FROM reserva r
    JOIN jornada_cocina j ON j.id_jornada = r.id_jornada
    JOIN menu_dia m ON m.id_menu = j.id_menu
    WHERE m.fecha >= CURRENT_DATE + INTERVAL '1 day'
);

COMMIT;
-- =========================================================
-- 23. RESERVAS "CONFIRMADA" PARA HOY
--     Usuarios manuales (3,7,8,9,10) + 50% dummies impares
-- =========================================================
BEGIN;

-- Dummies impares u <= 40 ya tienen reserva 'consumida' hoy → 'confirmada'
-- Borrar consumo asociado primero para evitar inconsistencias
DELETE FROM consumo
WHERE id_reserva IN (
    SELECT r.id_reserva
    FROM reserva r
    JOIN jornada_cocina jc ON jc.id_jornada = r.id_jornada
    JOIN menu_dia m ON m.id_menu = jc.id_menu
    WHERE m.fecha = CURRENT_DATE
      AND r.id_usuario % 2 = 1
      AND r.id_usuario BETWEEN 11 AND 40
      AND r.estado = 'consumida'
);

UPDATE reserva
SET estado = 'confirmada'
WHERE id_jornada = (
        SELECT jc.id_jornada FROM jornada_cocina jc
        JOIN menu_dia m ON m.id_menu = jc.id_menu
        WHERE m.fecha = CURRENT_DATE LIMIT 1
    )
  AND estado = 'consumida'
  AND id_usuario % 2 = 1
  AND id_usuario BETWEEN 11 AND 40;

-- Usuarios manuales funcionarios (IDs 3,7,8,9,10)
-- no entran en el loop del seed (que empieza en 11) → insertar ahora
INSERT INTO reserva (id_usuario, id_jornada, fecha_reserva, estado, id_plato_fondo)
SELECT
    u.id_usuario,
    jc.id_jornada,
    CURRENT_DATE + TIME '08:00:00',
    'confirmada',
    (SELECT md.id_plato FROM menu_detalle md
     WHERE md.id_menu = jc.id_menu AND md.orden IN (2, 3, 4)
     ORDER BY random() LIMIT 1)
FROM usuario u
CROSS JOIN (
    SELECT jc.id_jornada, jc.id_menu FROM jornada_cocina jc
    JOIN menu_dia m ON m.id_menu = jc.id_menu
    WHERE m.fecha = CURRENT_DATE LIMIT 1
) jc
WHERE u.id_usuario IN (3, 7, 8, 9, 10)
  AND NOT EXISTS (
      SELECT 1 FROM reserva r2
      JOIN jornada_cocina jc2 ON jc2.id_jornada = r2.id_jornada
      JOIN menu_dia m2 ON m2.id_menu = jc2.id_menu
      WHERE m2.fecha = CURRENT_DATE
        AND r2.id_usuario = u.id_usuario
  );

-- Recalcular raciones_disponibles de la jornada de hoy
UPDATE jornada_cocina
SET raciones_disponibles = raciones_planificadas - (
    SELECT COUNT(*) FROM reserva r
    WHERE r.id_jornada = jornada_cocina.id_jornada
      AND r.estado IN ('confirmada', 'consumida', 'retirada')
)
WHERE id_jornada = (
    SELECT jc.id_jornada FROM jornada_cocina jc
    JOIN menu_dia m ON m.id_menu = jc.id_menu
    WHERE m.fecha = CURRENT_DATE LIMIT 1
);

-- Ajustar secuencia de IDs
SELECT setval(
    pg_get_serial_sequence('reserva','id_reserva'),
    COALESCE((SELECT MAX(id_reserva) FROM reserva), 1),
    true
);

COMMIT;