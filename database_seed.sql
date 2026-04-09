-- 1. LIMPIEZA TOTAL
DELETE FROM merma_preparada; DELETE FROM merma_ingrediente; DELETE FROM consumo;
DELETE FROM reserva; DELETE FROM jornada_cocina; DELETE FROM menu_detalle;
DELETE FROM receta; DELETE FROM lote_ingrediente; DELETE FROM menu_dia;
DELETE FROM plato; DELETE FROM ingrediente; DELETE FROM usuario; DELETE FROM rol;

-- 2. ROLES
INSERT INTO rol (id_rol, nombre) VALUES (1, 'admin'), (2, 'cocina'), (3, 'funcionario');

-- 3. USUARIOS
INSERT INTO usuario (id_usuario, id_rol, rut, nombre, apellido, email, contrasena, faltas_acumuladas, estado) VALUES
(1, 1, '184562346', 'Ana', 'Rojas', 'ana.rojas@hospital.cl', '184562346', 0, 'activo'),
(2, 2, '227749806', 'Luis', 'Pérez', 'luis.perez@hospital.cl', '227749806', 0, 'activo'),
(3, 2, '205577648', 'Marta', 'Gómez', 'marta.gomez@hospital.cl', '205577648', 0, 'activo'),
(4, 3, '89905467', 'Carlos', 'Díaz', 'carlos.diaz@hospital.cl', '89905467', 0, 'activo'),
(5, 2, '123360094', 'Sofía', 'Mora', 'sofia.mora@hospital.cl', '123360094', 0, 'activo'),
(6, 1, '186634568', 'Pedro', 'Luna', 'pedro.luna@hospital.cl', '186634568', 0, 'activo'),
(7, 3, '130078975', 'Elena', 'Vega', 'elena.vega@hospital.cl', '130078975', 0, 'activo'),
(10, 3, '187746239', 'Diego', 'Fuentes', 'diego.fuentes@hospital.cl', '187746239', 0, 'activo'),
(11, 3, '150079984', 'Camila', 'Reyes', 'camila.reyes@hospital.cl', '150079984', 0, 'activo'),
(12, 3, '130963457', 'Jorge', 'Navarro', 'jorge.navarro@hospital.cl', '130963457', 0, 'activo');

-- 4. INGREDIENTES
INSERT INTO ingrediente (id_ingrediente, nombre, unidad_medida) VALUES
(1, 'Arroz', 'kg'), (2, 'Pollo', 'kg'), (3, 'Carne', 'kg'), (4, 'Tomate', 'kg'),
(5, 'Lechuga', 'unidad'), (6, 'Papa', 'kg'), (7, 'Aceite', 'lt'), (8, 'Sal', 'gr'),
(9, 'Harina', 'kg'), (10, 'Azúcar', 'gr'), (11, 'Tallarines', 'Kg'), (12, 'Lentejas', 'Kg');

-- 5. PLATOS
INSERT INTO plato (id_plato, nombre, tipo_plato, tipo_dieta) VALUES
(1, 'Ensalada Mixta', 'entrada', 'Normal'),
(2, 'Pollo con Arroz', 'fondo', 'Normal'),
(3, 'Carne con Papas', 'fondo', 'Normal'),
(4, 'Tarta de Manzana', 'postre', 'Normal'),
(5, 'Sopa del Día', 'entrada', 'Normal'),
(6, 'Budín de Pan', 'postre', 'Normal'),
(7, 'Lentejas', 'fondo', 'Normal'),
(8, 'Jalea', 'postre', 'Normal'),
(9, 'Lasaña de Verduras', 'fondo', 'Vegano'),
(10, 'Cazuela de Ave', 'entrada', 'Normal');

-- 6. MENÚS (30 DÍAS)
INSERT INTO menu_dia (id_menu, fecha, estado)
SELECT i, (CURRENT_DATE + (i || ' day')::interval)::date, 'activo'
FROM generate_series(1, 30) AS i;

-- 7. DETALLES DE MENÚ (UNA SOLA VEZ)
-- Bandeja 1
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 5, 1 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 2, 2 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 4, 3 FROM menu_dia;
-- Bandeja 2
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 1, 4 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 3, 5 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 6, 6 FROM menu_dia;
-- Bandeja 3
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 10, 7 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 9, 8 FROM menu_dia;
INSERT INTO menu_detalle (id_menu, id_plato, orden) SELECT id_menu, 8, 9 FROM menu_dia;

-- 8. JORNADAS (UNA SOLA VEZ - 3 OPCIONES POR DÍA)
INSERT INTO jornada_cocina (id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
SELECT (id_menu * 3), id_menu, 50, 50, 50 FROM menu_dia;

INSERT INTO jornada_cocina (id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
SELECT (id_menu * 3 + 1), id_menu, 50, 50, 50 FROM menu_dia;

INSERT INTO jornada_cocina (id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
SELECT (id_menu * 3 + 2), id_menu, 50, 50, 50 FROM menu_dia;