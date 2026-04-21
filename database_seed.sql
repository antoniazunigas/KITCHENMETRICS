-- 1. LIMPIEZA TOTAL (En orden de jerarquía)
DELETE FROM reserva; 
DELETE FROM jornada_cocina; 
DELETE FROM menu_detalle;
DELETE FROM receta; 
DELETE FROM menu_dia;
DELETE FROM plato; 
DELETE FROM ingrediente; 
DELETE FROM usuario; 
DELETE FROM rol;

-- 2. ROLES
INSERT INTO rol (id_rol, nombre) VALUES (1, 'admin'), (2, 'cocina'), (3, 'funcionario');

-- 3. USUARIOS (Sincronizados con tus datos originales)
INSERT INTO usuario (id_usuario, id_rol, rut, nombre, apellido, email, contrasena, faltas_acumuladas, estado) VALUES
(1, 1, '184562346', 'Ana', 'Rojas', 'ana.rojas@hospital.cl', '184562346', 0, 'activo'),
(2, 2, '227749806', 'Luis', 'Pérez', 'luis.perez@hospital.cl', '227749806', 0, 'activo'),
(3, 2, '205577648', 'Marta', 'Gómez', 'marta.gomez@hospital.cl', '205577648', 0, 'activo'),
(4, 3, '89905467', 'Carlos', 'Díaz', 'carlos.diaz@hospital.cl', '89905467', 0, 'activo'),
(5, 2, '123360094', 'Sofía', 'Mora', 'sofia.mora@hospital.cl', '123360094', 0, 'activo'),
(6, 1, '186634568', 'Pedro', 'Luna', 'pedro.luna@hospital.cl', '186634568', 0, 'activo'),
(7, 3, '130078975', 'Elena', 'Vega', 'elena.vega@hospital.cl', '130078975', 0, 'activo'),
<<<<<<< HEAD
(12, 3, '130963457', 'Jorge', 'Navarro', 'jorge.navarro@hospital.cl', '130963457', 0, 'activo');
=======
(10, 3, '187746239', 'Diego', 'Fuentes', 'diego.fuentes@hospital.cl', '187746239', 0, 'activo'),
(11, 3, '150079984', 'Camila', 'Reyes', 'camila.reyes@hospital.cl', '150079984', 0, 'activo'),
(12, 3, '130963457', 'Jorge', 'Navarro', 'jorge.navarro@hospital.cl', '130963457', 0, 'activo'),
(13, 2, '17.654.321-0', 'Claudia', 'Vera', 'claudia.vera@hospital.cl', '', 0, 'activo'),
(14, 2, '15.876.543-2', 'Jorge', 'Castro', 'jorge.castro@hospital.cl', '', 0, 'activo'),
(15, 2, '13.987.654-3', 'Andrea', 'Morales', 'andrea.morales@hospital.cl', '', 0, 'activo'),
(16, 2, '18.234.567-1', 'Ricardo', 'Núñez', 'ricardo.nunez@hospital.cl', '', 0, 'activo'),
(17, 2, '16.345.678-9', 'Valentina', 'Soto', 'valentina.soto@hospital.cl', '', 0, 'activo'),
(18, 2, '12.456.789-0', 'Francisco', 'Parra', 'francisco.parra@hospital.cl', '', 0, 'activo'),
(19, 2, '19.567.890-1', 'Daniela', 'Bravo', 'daniela.bravo@hospital.cl', '', 0, 'activo'),
(20, 2, '14.678.901-2', 'Martín', 'Herrera', 'martin.herrera@hospital.cl', '', 0, 'activo'),
(21, 2, '17.789.012-3', 'Gabriela', 'Fuentes', 'gabriela.fuentes@hospital.cl', '', 0, 'activo'),
(22, 3, '11.111.111-1', 'Carlos', 'Muñoz', 'carlos.munoz@hospital.cl', '', 0, 'activo'),
(23, 2, '13.456.789-0', 'Luis', 'Fernández R.', 'luis.fernandezr@hospital.cl', '', 0, 'activo'),
(24, 2, '19.012.345-6', 'Carmen', 'Torres', 'carmen.torres@hospital.cl', '', 0, 'activo'),
(25, 2, '11.234.567-8', 'Roberto', 'Díaz', 'roberto.diaz@hospital.cl', '', 0, 'activo');

>>>>>>> a9c2148242811b6e17126034a0d7123e4629ed13

-- 4. INGREDIENTES
INSERT INTO ingrediente (id_ingrediente, nombre, unidad_medida) VALUES
(1, 'Arroz', 'kg'), (2, 'Pollo', 'kg'), (3, 'Carne', 'kg'), (4, 'Tomate', 'kg'),
(5, 'Lechuga', 'unidad'), (6, 'Papa', 'kg'), (7, 'Aceite', 'lt'), (8, 'Sal', 'gr'),
<<<<<<< HEAD
(9, 'Harina', 'kg'), (11, 'Tallarines', 'Kg'), (12, 'Zapallo', 'kg'), (13, 'Lentejas', 'kg'), (14, 'Azúcar', 'gr');
=======
(9, 'Harina', 'kg'), (10, 'Azúcar', 'gr'), (11, 'Tallarines', 'Kg'), (12, 'Lentejas', 'Kg'),
(13, 'Pasta', 'kg'), (14, 'Leche Descremada', 'L'), (15, 'Queso Fresco', 'kg');
>>>>>>> a9c2148242811b6e17126034a0d7123e4629ed13

-- 5. PLATOS
INSERT INTO plato (id_plato, nombre, tipo_plato, tipo_dieta) VALUES
(1, 'Ensalada Mixta', 'entrada', 'Normal'),
(2, 'Pollo con Arroz', 'fondo', 'Normal'),
(3, 'Carne con Papas', 'fondo', 'Normal'),
(4, 'Tarta de Manzana', 'postre', 'Normal'),
(5, 'Sopa del Día', 'entrada', 'Normal'),
(6, 'Budín de Pan', 'postre', 'Normal'),
(7, 'Lentejas Guisadas', 'fondo', 'Vegano'),
(8, 'Jalea de Frutas', 'postre', 'Normal'),
(9, 'Lasaña de Verduras', 'fondo', 'Vegano'),
<<<<<<< HEAD
(10, 'Cazuela de Ave', 'fondo', 'Normal'),
(12, 'Crema de Verduras', 'entrada', 'Normal');

-- 6. RECETAS (Cálculo automático de insumos)
-- Fondos
INSERT INTO receta (id_plato, id_ingrediente, cantidad_por_porcion) VALUES 
(2, 2, 0.250), (2, 1, 0.100), -- Pollo Arroz
(10, 2, 0.200), (10, 12, 0.150), -- Cazuela
(3, 3, 0.200), (3, 6, 0.300), -- Carne Papas
(9, 9, 0.150), (9, 4, 0.200), -- Lasaña
(7, 13, 0.150), (7, 1, 0.050); -- Lentejas
-- Entradas y Postres
INSERT INTO receta (id_plato, id_ingrediente, cantidad_por_porcion) VALUES 
(1, 5, 0.500), (1, 4, 0.100), -- Ensalada
(5, 6, 0.100), (12, 12, 0.150), -- Sopa y Crema
(4, 14, 0.050), (6, 14, 0.050); -- Postres (Azúcar)

-- 7. MENÚS (30 DÍAS)
INSERT INTO menu_dia (id_menu, fecha, estado)
SELECT i, (CURRENT_DATE + (i || ' day')::interval)::date, 'activo'
FROM generate_series(1, 30) AS i;

-- 8. DETALLES DE MENÚ (Rotación coherente por dieta)
-- BANDEJA 1 (Normal): Rota Pollo (2) / Cazuela (10)
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 5, 0 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) 
SELECT id_menu, CASE WHEN id_menu % 2 = 0 THEN 2 ELSE 10 END, 1 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 4, 2 FROM menu_dia;

-- BANDEJA 2 (Normal): Carne con Papas (3)
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 1, 3 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 3, 4 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 6, 5 FROM menu_dia;

-- BANDEJA 3 (Vegana): Rota Lasaña (9) / Lentejas (7)
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 12, 6 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) 
SELECT id_menu, CASE WHEN id_menu % 2 = 0 THEN 9 ELSE 7 END, 7 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 8, 8 FROM menu_dia;

-- 9. JORNADAS
INSERT INTO jornada_cocina (id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
SELECT (id_menu * 3), id_menu, 50, 50, 50 FROM menu_dia;
INSERT INTO jornada_cocina (id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
SELECT (id_menu * 3 + 1), id_menu, 50, 50, 50 FROM menu_dia;
INSERT INTO jornada_cocina (id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
SELECT (id_menu * 3 + 2), id_menu, 50, 50, 50 FROM menu_dia;
=======
(10, 'Cazuela de Ave', 'entrada', 'Normal'),
(11, 'Gelatina', 'postre', 'Blanda'),
(12, 'Pasta Boloñesa', 'Principal', 'normal'),
(13, 'Pan Integral', 'Acompañamiento', NULL),
(14, 'Sopa de Verduras', 'Sopa', 'blanda'),
(15, 'Ensalada Caprese', 'Ensalada', NULL);

-- 6. MENÚS BASE
INSERT INTO menu_dia (id_menu, fecha, estado) VALUES
(1, '2026-04-15', 'activo'),
(2, '2026-04-14', 'activo'),
(3, '2026-04-11', 'activo'),
(4, '2026-04-10', 'activo'),
(5, '2026-04-09', 'activo'),
(6, '2026-04-08', 'activo'),
(7, '2026-04-07', 'activo'),
(8, '2026-04-04', 'activo'),
(9, '2026-04-03', 'activo'),
(10, '2026-04-02', 'activo'),
(11, '2026-04-01', 'activo')
ON CONFLICT (id_menu) DO NOTHING;

-- 7. DETALLES DE MENÚ BASE
INSERT INTO menu_detalle (id_menu_detalle, id_menu, id_plato, orden) VALUES
(1, 1, 1, 1), (2, 1, 2, 2), (3, 1, 3, 3), (4, 1, 4, 4),
(5, 2, 5, 1), (6, 2, 6, 2), (7, 2, 7, 3), (8, 2, 8, 4),
(9, 3, 9, 1), (10, 3, 10, 2), (11, 3, 3, 3), (12, 3, 11, 4),
(13, 4, 12, 1), (14, 4, 3, 2), (15, 4, 13, 3), (16, 4, 4, 4)
ON CONFLICT (id_menu_detalle) DO NOTHING;

-- 8. JORNADAS BASE
INSERT INTO jornada_cocina (id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles) VALUES
(1, 1, 165, 160, 16), (2, 2, 170, 168, 20), (3, 3, 155, 152, 20),
(4, 4, 160, 158, 22), (5, 5, 158, 155, 15), (6, 6, 161, 158, 13),
(7, 7, 156, 153, 11), (8, 8, 139, 136, 11), (9, 9, 148, 145, 14),
(10, 10, 152, 150, 12), (11, 11, 145, 142, 14)
ON CONFLICT (id_jornada) DO NOTHING;

-- 9. LOTES DE INGREDIENTES
INSERT INTO lote_ingrediente (id_lote, id_ingrediente, fecha_ingreso, fecha_vencimiento, cantidad_inicial, cantidad_disponible, costo_unitario) VALUES
(1, 1, '2026-04-01', '2026-07-01', 60.0, 45.5, 1500),
(2, 2, '2026-04-10', '2026-04-25', 40.0, 28.2, 9000),
(3, 3, '2026-04-12', '2026-04-22', 20.0, 8.3, 1500),
(4, 4, '2026-04-08', '2026-05-08', 25.0, 15.7, 1200),
(5, 5, '2026-04-09', '2026-05-09', 20.0, 12.4, 1200),
(6, 6, '2026-04-05', '2026-06-05', 70.0, 52.1, 800),
(7, 7, '2026-04-01', '2026-10-01', 25.0, 18.5, 5000),
(8, 8, '2026-04-15', '2027-04-15', 10.0, 6.2, 800),
(9, 9, '2026-04-02', '2026-10-02', 30.0, 22.8, 2000),
(10, 10, '2026-04-03', '2026-10-03', 45.0, 34.6, 2000),
(11, 11, '2026-04-14', '2026-04-18', 20.0, 12.5, 2000),
(12, 12, '2026-04-13', '2026-04-19', 8.0, 5.4, 10000),
(13, 13, '2026-04-11', '2026-04-20', 25.0, 18.7, 8000),
(14, 14, '2026-04-12', '2026-04-21', 20.0, 14.3, 8000),
(15, 15, '2026-04-14', '2026-04-20', 12.0, 6.8, 1500)
ON CONFLICT (id_lote) DO NOTHING;

-- 10. RECETAS
INSERT INTO receta (id_receta, id_plato, id_ingrediente, cantidad_por_porcion) VALUES
(1, 1, 2, 0.200), (2, 1, 4, 0.050), (3, 1, 7, 0.015),
(4, 2, 1, 0.100), (5, 2, 7, 0.010), (6, 3, 3, 0.080),
(7, 3, 15, 0.060), (8, 3, 4, 0.030), (9, 12, 10, 0.120),
(10, 12, 13, 0.100), (11, 12, 3, 0.050)
ON CONFLICT (id_receta) DO NOTHING;

-- 11. RESERVAS BASE
INSERT INTO reserva (id_reserva, id_usuario, id_jornada, fecha_reserva, estado) VALUES
(1, 22, 1, '2026-04-15T08:00:00', 'confirmada'), (2, 2, 1, '2026-04-15T08:15:00', 'confirmada'),
(3, 3, 1, '2026-04-15T08:30:00', 'confirmada'), (4, 10, 1, '2026-04-15T09:00:00', 'consumida'),
(5, 5, 1, '2026-04-15T09:15:00', 'no_consumida'), (6, 6, 2, '2026-04-14T08:00:00', 'consumida'),
(7, 23, 2, '2026-04-14T08:30:00', 'consumida'), (8, 24, 2, '2026-04-14T09:00:00', 'cancelada'),
(9, 25, 2, '2026-04-14T09:30:00', 'no_consumida'), (10, 11, 3, '2026-04-13T08:00:00', 'consumida'),
(11, 12, 3, '2026-04-13T08:30:00', 'consumida'), (12, 13, 3, '2026-04-13T09:00:00', 'confirmada'),
(13, 14, 4, '2026-04-12T08:00:00', 'cancelada'), (14, 15, 4, '2026-04-12T08:30:00', 'consumida'),
(15, 16, 4, '2026-04-12T09:00:00', 'consumida'), (16, 17, 3, '2026-04-11T08:00:00', 'no_consumida'),
(17, 18, 3, '2026-04-11T09:00:00', 'consumida'), (18, 19, 3, '2026-04-11T09:30:00', 'consumida'),
(19, 20, 4, '2026-04-10T08:00:00', 'confirmada'), (20, 21, 4, '2026-04-10T08:30:00', 'consumida')
ON CONFLICT (id_reserva) DO NOTHING;

-- 12. CONSUMOS BASE
INSERT INTO consumo (id_consumo, id_reserva, id_jornada, fecha_consumo, estado) VALUES
(1, 4, 1, '2026-04-15T12:30:00', 'registrado'), (2, 6, 2, '2026-04-14T12:15:00', 'registrado'),
(3, 7, 2, '2026-04-14T12:30:00', 'registrado'), (4, 10, 3, '2026-04-13T12:00:00', 'registrado'),
(5, 11, 3, '2026-04-13T12:15:00', 'registrado'), (6, 14, 4, '2026-04-12T12:00:00', 'registrado'),
(7, 15, 4, '2026-04-12T12:30:00', 'registrado'), (8, 17, 3, '2026-04-11T12:15:00', 'registrado'),
(9, 18, 3, '2026-04-11T12:45:00', 'registrado'), (10, 20, 4, '2026-04-10T12:30:00', 'registrado')
ON CONFLICT (id_consumo) DO NOTHING;

-- 13. MERMA_INGREDIENTE BASE
INSERT INTO merma_ingrediente (id_merma_ing, id_lote, fecha, cantidad, costo_perdido, motivo) VALUES
(1, 3, '2026-04-15', 0.3, 450, 'vencimiento'), (2, 15, '2026-04-14', 0.2, 300, 'deterioro'),
(3, 2, '2026-04-11', 0.3, 2700, 'deterioro'), (4, 6, '2026-04-10', 0.1, 80, 'contaminacion'),
(5, 1, '2026-04-09', 0.3, 450, 'sobrante'), (6, 4, '2026-04-08', 0.3, 360, 'error_preparacion'),
(7, 5, '2026-04-07', 0.2, 240, 'sobrante'), (8, 10, '2026-04-04', 0.4, 800, 'vencimiento'),
(9, 7, '2026-04-03', 0.1, 500, 'contaminacion'), (10, 9, '2026-04-02', 0.1, 200, 'sobrante'),
(11, 1, '2026-04-01', 0.1, 150, 'sobrante'), (12, 1, '2026-03-12', 0.1, 150, 'vencimiento'),
(13, 3, '2026-03-11', 0.1, 150, 'deterioro'), (14, 6, '2026-03-10', 0.1, 80, 'sobrante'),
(15, 2, '2026-03-09', 0.2, 1800, 'deterioro'), (16, 4, '2026-03-08', 0.1, 120, 'vencimiento'),
(17, 7, '2026-03-05', 0.1, 500, 'contaminacion'), (18, 10, '2026-03-04', 0.1, 200, 'error_preparacion'),
(19, 5, '2026-03-03', 0.1, 120, 'vencimiento'), (20, 1, '2026-03-02', 0.1, 150, 'sobrante'),
(21, 9, '2026-03-01', 0.2, 400, 'vencimiento')
ON CONFLICT (id_merma_ing) DO NOTHING;

-- 14. MERMA_PREPARADA BASE
INSERT INTO merma_preparada (id_merma_prep, id_jornada, fecha, cantidad_raciones, costo_perdido, motivo) VALUES
(1, 1, '2026-04-15', 12, 24000, 'sobrante'), (2, 2, '2026-04-14', 15, 30000, 'sobrante'),
(3, 3, '2026-04-11', 18, 36000, 'sobrante'), (4, 4, '2026-04-10', 14, 28000, 'sobrante'),
(5, 5, '2026-04-09', 16, 32000, 'sobrante'), (6, 6, '2026-04-08', 13, 26000, 'sobrante'),
(7, 7, '2026-04-07', 10, 20000, 'sobrante'), (8, 8, '2026-04-04', 8, 16000, 'sobrante'),
(9, 9, '2026-04-03', 11, 22000, 'error_preparacion'), (10, 10, '2026-04-02', 9, 18000, 'sobrante'),
(11, 11, '2026-04-01', 14, 28000, 'sobrante')
ON CONFLICT (id_merma_prep) DO NOTHING;


-- =========================================================================
-- 15. BLOQUE DE GENERACIÓN MASIVA (18 de Marzo al 17 de Abril) 
-- Generación de 140 dummies + Faltas aleatorias (1-15) + Reservas diarias
-- =========================================================================
DO $$
DECLARE
    v_fecha DATE;
    v_id_menu INT := 12;
    v_id_jornada INT := 12;
    v_id_reserva INT := 21;
    v_id_consumo INT := 11;
    v_id_merma_prep INT := 12;
    u INT;
    v_planificadas INT := 160; -- Ajustado para soportar el flujo de usuarios
    v_preparadas   INT;
    v_disponibles  INT;
    v_merma        INT;
    v_no_consumidas INT;
    v_faltas INT;
    v_estado TEXT;
BEGIN
    -- A) GENERAR 140 USUARIOS DUMMY (IDs del 11 al 150)
    -- Con faltas acumuladas aleatorias entre 1 y 15
    FOR u IN 11..150 LOOP
        v_faltas := floor(random() * 15 + 1)::int; -- Faltas aleatorias de 1 a 15
        v_estado := CASE WHEN v_faltas >= 3 THEN 'bloqueado' ELSE 'activo' END;

        INSERT INTO usuario (id_usuario, id_rol, rut, nombre, apellido, email, contrasena, faltas_acumuladas, estado)
        VALUES (
            u, 
            3, 
            '10000' || u, 
            'Usuario_' || u, 
            'Prueba', 
            'user' || u || '@hospital.cl', 
            'pass' || u, 
            v_faltas, 
            v_estado
        )
        ON CONFLICT (id_usuario) DO NOTHING;
    END LOOP;

    -- B) ITERACIÓN DIARIA (30 DÍAS)
    FOR v_fecha IN SELECT generate_series('2026-03-18'::DATE, '2026-04-17'::DATE, '1 day'::interval)
    LOOP
        -- Crear Menú
        INSERT INTO menu_dia (id_menu, fecha, estado) VALUES (v_id_menu, v_fecha, 'activo');
        
        -- Cálculo de raciones
        v_preparadas := ROUND(v_planificadas * (1 - (0.05 + random() * 0.05)));
        v_disponibles := v_planificadas - v_preparadas;

        -- Crear Jornada
        INSERT INTO jornada_cocina (id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
        VALUES (v_id_jornada, v_id_menu, v_planificadas, v_preparadas, v_disponibles);

        -- 1. Crear 100 Reservas que SÍ consumen (usando usuarios del 11 al 110)
        FOR u IN 11..110 LOOP
            INSERT INTO reserva (id_reserva, id_usuario, id_jornada, fecha_reserva, estado)
            VALUES (v_id_reserva, u, v_id_jornada, v_fecha + time '08:00:00', 'consumida');

            INSERT INTO consumo (id_consumo, id_reserva, id_jornada, fecha_consumo, estado)
            VALUES (v_id_consumo, v_id_reserva, v_id_jornada, v_fecha + time '12:30:00', 'registrado');

            v_id_reserva := v_id_reserva + 1;
            v_id_consumo := v_id_consumo + 1;
        END LOOP;

        -- 2. Crear entre 1 y 15 Reservas NO CONSUMIDAS (usando usuarios del 111 en adelante)
        v_no_consumidas := floor(random() * 15 + 1)::int;
        
        FOR u IN 111..(110 + v_no_consumidas) LOOP
            INSERT INTO reserva (id_reserva, id_usuario, id_jornada, fecha_reserva, estado)
            VALUES (v_id_reserva, u, v_id_jornada, v_fecha + time '08:30:00', 'no_consumida');
            
            v_id_reserva := v_id_reserva + 1;
        END LOOP;

        -- 3. Merma preparada del día
        v_merma := ROUND(v_preparadas * (0.05 + random() * 0.05));
        INSERT INTO merma_preparada (id_merma_prep, id_jornada, fecha, cantidad_raciones, costo_perdido, motivo)
        VALUES (v_id_merma_prep, v_id_jornada, v_fecha, v_merma, v_merma * 1500, 'sobrante');
        
        -- Incrementar IDs para la siguiente fecha
        v_id_menu := v_id_menu + 1;
        v_id_jornada := v_id_jornada + 1;
        v_id_merma_prep := v_id_merma_prep + 1;
    END LOOP;
END $$;




-- 16. ACTUALIZACIÓN DE SECUENCIAS
SELECT setval(pg_get_serial_sequence('rol','id_rol'), COALESCE((SELECT MAX(id_rol) FROM rol), 1), true);
SELECT setval(pg_get_serial_sequence('usuario','id_usuario'), COALESCE((SELECT MAX(id_usuario) FROM usuario), 1), true);
SELECT setval(pg_get_serial_sequence('ingrediente','id_ingrediente'), COALESCE((SELECT MAX(id_ingrediente) FROM ingrediente), 1), true);
SELECT setval(pg_get_serial_sequence('plato','id_plato'), COALESCE((SELECT MAX(id_plato) FROM plato), 1), true);
SELECT setval(pg_get_serial_sequence('menu_dia','id_menu'), COALESCE((SELECT MAX(id_menu) FROM menu_dia), 1), true);
SELECT setval(pg_get_serial_sequence('menu_detalle','id_menu_detalle'), COALESCE((SELECT MAX(id_menu_detalle) FROM menu_detalle), 1), true);
SELECT setval(pg_get_serial_sequence('jornada_cocina','id_jornada'), COALESCE((SELECT MAX(id_jornada) FROM jornada_cocina), 1), true);
SELECT setval(pg_get_serial_sequence('lote_ingrediente','id_lote'), COALESCE((SELECT MAX(id_lote) FROM lote_ingrediente), 1), true);
SELECT setval(pg_get_serial_sequence('receta','id_receta'), COALESCE((SELECT MAX(id_receta) FROM receta), 1), true);
SELECT setval(pg_get_serial_sequence('reserva','id_reserva'), COALESCE((SELECT MAX(id_reserva) FROM reserva), 1), true);
SELECT setval(pg_get_serial_sequence('consumo','id_consumo'), COALESCE((SELECT MAX(id_consumo) FROM consumo), 1), true);
SELECT setval(pg_get_serial_sequence('merma_ingrediente','id_merma_ing'), COALESCE((SELECT MAX(id_merma_ing) FROM merma_ingrediente), 1), true);
SELECT setval(pg_get_serial_sequence('merma_preparada','id_merma_prep'), COALESCE((SELECT MAX(id_merma_prep) FROM merma_preparada), 1), true);
>>>>>>> a9c2148242811b6e17126034a0d7123e4629ed13
