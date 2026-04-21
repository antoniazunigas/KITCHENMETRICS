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
(12, 3, '130963457', 'Jorge', 'Navarro', 'jorge.navarro@hospital.cl', '130963457', 0, 'activo');

-- 4. INGREDIENTES
INSERT INTO ingrediente (id_ingrediente, nombre, unidad_medida) VALUES
(1, 'Arroz', 'kg'), (2, 'Pollo', 'kg'), (3, 'Carne', 'kg'), (4, 'Tomate', 'kg'),
(5, 'Lechuga', 'unidad'), (6, 'Papa', 'kg'), (7, 'Aceite', 'lt'), (8, 'Sal', 'gr'),
(9, 'Harina', 'kg'), (11, 'Tallarines', 'Kg'), (12, 'Zapallo', 'kg'), (13, 'Lentejas', 'kg'), (14, 'Azúcar', 'gr');

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