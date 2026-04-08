-- database_seed.sql

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

-- BEGIN
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_rol';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_usuario';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_menu_dia';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_plato';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_menu_detalle';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_ingrediente';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_lote_ingrediente';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_receta';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_jornada_cocina';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_reserva';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_consumo';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_merma_ingrediente';
--    EXECUTE IMMEDIATE 'DROP SEQUENCE seq_merma_preparada';
-- EXCEPTION WHEN OTHERS THEN NULL;
-- END;
-- /

-- CREATE SEQUENCE seq_rol START WITH 1;
-- CREATE SEQUENCE seq_usuario START WITH 1;
-- CREATE SEQUENCE seq_menu_dia START WITH 1;
-- CREATE SEQUENCE seq_plato START WITH 1;
-- CREATE SEQUENCE seq_menu_detalle START WITH 1;
-- CREATE SEQUENCE seq_ingrediente START WITH 1;
-- CREATE SEQUENCE seq_lote_ingrediente START WITH 1;
-- CREATE SEQUENCE seq_receta START WITH 1;
-- CREATE SEQUENCE seq_jornada_cocina START WITH 1;
-- CREATE SEQUENCE seq_reserva START WITH 1;
-- CREATE SEQUENCE seq_consumo START WITH 1;
-- CREATE SEQUENCE seq_merma_ingrediente START WITH 1;
-- CREATE SEQUENCE seq_merma_preparada START WITH 1;

-- ROLES
INSERT INTO rol (id_rol, nombre) VALUES
(1, 'admin'),
(2, 'cocina'),
(3, 'funcionario'),
(4, 'otro');

-- USUARIOS
INSERT INTO usuario
(id_usuario, id_rol, rut, nombre, apellido, email, contrasena, faltas_acumuladas, estado)
VALUES
(1, 1, '111111111', 'Ana', 'Rojas', 'ana.rojas@mail.com', '1234', 0, 'activo'),
(2, 2, '222222222', 'Luis', 'Pérez', 'luis.perez@mail.com', '1234', 0, 'activo'),
(3, 2, '333333333', 'Marta', 'Gómez', 'marta.gomez@mail.com', '1234', 1, 'activo'),
(4, 3, '444444444', 'Carlos', 'Díaz', 'carlos.diaz@mail.com', '1234', 0, 'activo'),
(5, 3, '555555555', 'Sofía', 'Mora', 'sofia.mora@mail.com', '1234', 2, 'activo'),
(6, 3, '666666666', 'Pedro', 'Luna', 'pedro.luna@mail.com', '1234', 0, 'activo'),
(7, 4, '777777777', 'Elena', 'Vega', 'elena.vega@mail.com', '1234', 0, 'activo'),
(8, 4, '888888888', 'Tomás', 'Silva', 'tomas.silva@mail.com', '1234', 0, 'activo'),
(9, 4, '999999999', 'Paula', 'León', 'paula.leon@mail.com', '1234', 3, 'bloqueado'),
(10, 4, '101010101', 'Diego', 'Fuentes', 'diego.fuentes@mail.com', '1234', 0, 'activo'),
(11, 4, '121212121', 'Camila', 'Reyes', 'camila.reyes@mail.com', '1234', 1, 'activo'),
(12, 4, '131313131', 'Jorge', 'Navarro', 'jorge.navarro@mail.com', '1234', 0, 'activo');

-- INGREDIENTES
INSERT INTO ingrediente (id_ingrediente, nombre, unidad_medida) VALUES
(1, 'Arroz', 'kg'),
(2, 'Pollo', 'kg'),
(3, 'Carne', 'kg'),
(4, 'Tomate', 'kg'),
(5, 'Lechuga', 'unidad'),
(6, 'Papa', 'kg'),
(7, 'Aceite', 'lt'),
(8, 'Sal', 'gr'),
(9, 'Harina', 'kg'),
(10, 'Azúcar', 'gr');

-- LOTES
INSERT INTO lote_ingrediente
(id_lote, id_ingrediente, fecha_ingreso, fecha_vencimiento, cantidad_inicial, cantidad_disponible, costo_unitario)
VALUES
(1, 1, '2026-03-20', '2026-05-20', 50.000, 44.500, 980.00),
(2, 1, '2026-03-28', '2026-05-28', 40.000, 40.000, 1020.00),
(3, 2, '2026-03-18', '2026-04-18', 35.000, 20.000, 4200.00),
(4, 2, '2026-03-29', '2026-04-29', 30.000, 30.000, 4300.00),
(5, 3, '2026-03-17', '2026-04-17', 25.000, 12.000, 5900.00),
(6, 4, '2026-03-21', '2026-04-21', 20.000, 14.500, 1500.00),
(7, 5, '2026-03-22', '2026-04-22', 50.000, 47.000, 350.00),
(8, 6, '2026-03-19', '2026-04-19', 60.000, 33.000, 900.00),
(9, 7, '2026-03-25', '2026-06-25', 15.000, 15.000, 2100.00),
(10, 8, '2026-03-24', '2026-06-24', 10.000, 9.500, 800.00),
(11, 9, '2026-03-23', '2026-05-23', 45.000, 40.000, 1100.00),
(12, 10, '2026-03-26', '2026-05-26', 12.000, 12.000, 1700.00);

-- PLATOS
INSERT INTO plato (id_plato, nombre, tipo_plato) VALUES
(1, 'Ensalada Mixta', 'entrada'),
(2, 'Pollo con Arroz', 'fondo'),
(3, 'Carne con Papas', 'fondo'),
(4, 'Tarta de Manzana', 'postre'),
(5, 'Sopa del Día', 'entrada'),
(6, 'Budín de Pan', 'postre');

-- RECETAS
INSERT INTO receta (id_receta, id_plato, id_ingrediente, cantidad_por_porcion) VALUES
(1, 1, 4, 0.080),
(2, 1, 5, 0.200),
(3, 1, 8, 0.005),

(4, 2, 1, 0.180),
(5, 2, 2, 0.220),
(6, 2, 7, 0.010),

(7, 3, 3, 0.250),
(8, 3, 6, 0.200),
(9, 3, 8, 0.005),

(10, 4, 9, 0.120),
(11, 4, 10, 0.050),
(12, 4, 7, 0.008),

(13, 5, 4, 0.060),
(14, 5, 6, 0.100),
(15, 5, 8, 0.004),

(16, 6, 9, 0.150),
(17, 6, 10, 0.070),
(18, 6, 7, 0.006);

-- MENÚS DEL DÍA
INSERT INTO menu_dia (id_menu, fecha, estado) VALUES
(1, '2026-04-01', 'cerrado'),
(2, '2026-04-02', 'cerrado'),
(3, '2026-04-03', 'activo'),
(4, '2026-04-04', 'activo'),
(5, '2026-04-05', 'borrador');

-- DETALLE DE MENÚ
INSERT INTO menu_detalle (id_menu_detalle, id_menu, id_plato, orden) VALUES
(1, 1, 5, 1),
(2, 1, 2, 2),
(3, 1, 4, 3),

(4, 2, 1, 1),
(5, 2, 3, 2),
(6, 2, 6, 3),

(7, 3, 5, 1),
(8, 3, 2, 2),
(9, 3, 4, 3),

(10, 4, 1, 1),
(11, 4, 3, 2),
(12, 4, 6, 3),

(13, 5, 5, 1),
(14, 5, 2, 2),
(15, 5, 4, 3);

-- JORNADAS
INSERT INTO jornada_cocina
(id_jornada, id_menu, raciones_planificadas, raciones_preparadas, raciones_disponibles)
VALUES
(1, 1, 50, 48, 12),
(2, 2, 55, 55, 18),
(3, 3, 60, 58, 20),
(4, 4, 45, 45, 15),
(5, 5, 70, 70, 70);

-- RESERVAS
INSERT INTO reserva
(id_reserva, id_usuario, id_jornada, fecha_reserva, estado)
VALUES
(1, 7, 1, '2026-03-31 08:10:00', 'consumida'),
(2, 8, 1, '2026-03-31 08:12:00', 'consumida'),
(3, 10, 1, '2026-03-31 08:14:00', 'cancelada'),
(4, 11, 1, '2026-03-31 08:16:00', 'consumida'),
(5, 12, 1, '2026-03-31 08:18:00', 'no_retirada'),

(6, 7, 2, '2026-04-01 08:10:00', 'consumida'),
(7, 8, 2, '2026-04-01 08:12:00', 'consumida'),
(8, 10, 2, '2026-04-01 08:14:00', 'consumida'),
(9, 11, 2, '2026-04-01 08:16:00', 'cancelada'),
(10, 12, 2, '2026-04-01 08:18:00', 'consumida'),

(11, 7, 3, '2026-04-02 08:10:00', 'consumida'),
(12, 8, 3, '2026-04-02 08:12:00', 'consumida'),
(13, 10, 3, '2026-04-02 08:14:00', 'consumida'),
(14, 11, 3, '2026-04-02 08:16:00', 'consumida'),
(15, 12, 3, '2026-04-02 08:18:00', 'cancelada'),

(16, 7, 4, '2026-04-03 08:10:00', 'consumida'),
(17, 8, 4, '2026-04-03 08:12:00', 'no_retirada'),
(18, 10, 4, '2026-04-03 08:14:00', 'consumida'),
(19, 11, 4, '2026-04-03 08:16:00', 'consumida'),
(20, 12, 4, '2026-04-03 08:18:00', 'consumida');

-- CONSUMOS
INSERT INTO consumo
(id_consumo, id_reserva, id_jornada, fecha_consumo, estado)
VALUES
(1, 1, 1, '2026-03-31 12:15:00', 'registrado'),
(2, 2, 1, '2026-03-31 12:16:00', 'registrado'),
(3, 4, 1, '2026-03-31 12:18:00', 'registrado'),

(4, 6, 2, '2026-04-01 12:15:00', 'registrado'),
(5, 7, 2, '2026-04-01 12:16:00', 'registrado'),
(6, 8, 2, '2026-04-01 12:17:00', 'registrado'),
(7, 10, 2, '2026-04-01 12:18:00', 'registrado'),

(8, 11, 3, '2026-04-02 12:15:00', 'registrado'),
(9, 12, 3, '2026-04-02 12:16:00', 'registrado'),
(10, 13, 3, '2026-04-02 12:17:00', 'registrado'),
(11, 14, 3, '2026-04-02 12:18:00', 'registrado'),

(12, 16, 4, '2026-04-03 12:15:00', 'registrado'),
(13, 18, 4, '2026-04-03 12:16:00', 'registrado'),
(14, 19, 4, '2026-04-03 12:17:00', 'registrado'),
(15, 20, 4, '2026-04-03 12:18:00', 'registrado');

-- MERMAS DE INGREDIENTES
INSERT INTO merma_ingrediente
(id_merma_ing, id_lote, fecha, cantidad, costo_perdido, motivo)
VALUES
(1, 3, '2026-04-05', 2.000, 8600.00, 'vencimiento'),
(2, 5, '2026-04-05', 1.500, 8850.00, 'deterioro'),
(3, 8, '2026-04-04', 3.000, 2700.00, 'manipulacion'),
(4, 10, '2026-04-04', 0.500, 400.00, 'vencimiento');

-- MERMAS DE PREPARADOS
INSERT INTO merma_preparada
(id_merma_prep, id_jornada, fecha, cantidad_raciones, costo_perdido, motivo)
VALUES
(1, 1, '2026-03-31', 4, 12000.00, 'sobrante'),
(2, 2, '2026-04-01', 3, 9500.00, 'sobrante'),
(3, 4, '2026-04-03', 2, 6400.00, 'cancelacion');