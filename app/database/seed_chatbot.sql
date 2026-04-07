-- ==========================================================
-- seed_chatbot.sql
-- ==========================================================
-- Seed mínimo para soportar y validar la funcionalidad ChatBot.
--
-- Objetivo del seed (cobertura de comandos):
--   - /stats       : existir Pokémon con estadísticas en tabla Pokemon
--   - /compare     : existir al menos 2 Pokémon con estadísticas
--   - /score_team  : existir un equipo demo con 3 Pokémon asociados
--   - /weaknesses  : existir tipos + relaciones especie-tipo + debilidades
--   - /evolution   : existir cadena evolutiva (bulbasaur -> ivysaur -> venusaur)
--   - Casos especiales: nombre con carácter especial "porygon-z"
--
-- Notas:
--   - Se usa INSERT OR IGNORE para que el seed sea idempotente
--     (puede ejecutarse múltiples veces sin duplicar datos).
--   - Se crean únicamente los registros mínimos necesarios para los tests.
-- ==========================================================


-- ==========================================================
-- 1) USUARIO ADMIN (necesario para /score_team)
-- ==========================================================
-- Asegurar admin (por si schema no lo inserta o se reinicia la BD).
INSERT OR IGNORE INTO Usuario (IDUsuario, Nombre, Email, Contrasena, Estado, IDFavorito)
VALUES (1, 'admin', 'admin@admin.com', 'admin', 'Admin', 1);


-- ==========================================================
-- 2) ESPECIES (mínimas para /evolution y referencias de Pokemon)
-- ==========================================================
-- Cadena evolutiva:
--   bulbasaur (1) -> ivysaur (2) -> venusaur (3)
-- Además:
--   pikachu (25) para /stats y /compare
--   porygon-z (474) para probar caracteres especiales
INSERT OR IGNORE INTO Especie
(PokedexID, Nombre, EsLegendario, Generacion, Sprite, NombreItem, Descripcion,
 Altura, Peso, Categoria, TieneEvolucion, Prevolucion)
VALUES
(1,   'bulbasaur', 0, 1, 'None', 'None', 'Seed',  7.0,   69.0,   'Seed', 1, NULL),
(2,   'ivysaur',   0, 1, 'None', 'None', 'Seed', 10.0,  130.0,   'Seed', 1, 1),
(3,   'venusaur',  0, 1, 'None', 'None', 'Seed', 20.0, 1000.0,   'Seed', 0, 2),
(25,  'pikachu',   0, 1, 'None', 'None', 'Seed',  4.0,   60.0,   'Seed', 0, NULL),
(474, 'porygon-z', 0, 4, 'None', 'None', 'Seed',  9.0,   34.0,   'Seed', 0, NULL);


-- ==========================================================
-- 3) TIPOS + RELACIONES ESPECIE-TIPO (necesario para /weaknesses)
-- ==========================================================
-- Inserción de tipos mínimos usados en debilidades/fortalezas y asignación a especies.
INSERT OR IGNORE INTO Tipo (Nombre) VALUES
('planta'), ('veneno'), ('electrico'),
('fuego'), ('hielo'), ('volador'), ('psiquico'),
('agua'), ('hada'), ('normal');

-- Bulbasaur: planta + veneno
INSERT OR IGNORE INTO REspecieTipo (NombreTipo, PokedexID) VALUES
('planta', 1),
('veneno', 1);

-- Pikachu: eléctrico
INSERT OR IGNORE INTO REspecieTipo (NombreTipo, PokedexID) VALUES
('electrico', 25);

-- Porygon-Z: normal (simplificación para el seed)
INSERT OR IGNORE INTO REspecieTipo (NombreTipo, PokedexID) VALUES
('normal', 474);


-- ==========================================================
-- 4) DEBILIDADES / FORTALEZAS (tabla Debil)
-- ==========================================================
-- Debil(NombreTipoDebil, NombreTipoFuerte)
-- Interpretación:
--   - NombreTipoDebil  : tipo del Pokémon
--   - NombreTipoFuerte : tipo que le hace daño (contra el que es débil)
--
-- Debilidades mínimas para que /weaknesses devuelva valores.
INSERT OR IGNORE INTO Debil (NombreTipoDebil, NombreTipoFuerte) VALUES
('planta', 'fuego'),
('planta', 'hielo'),
('planta', 'volador'),
('veneno', 'psiquico');

-- Fortalezas:
-- En esta implementación, las "fortalezas" se derivan como el inverso:
-- si X es débil contra Y, entonces Y es fuerte contra X.
-- Por eso, para que "planta" salga fuerte contra "agua" se inserta (agua, planta).
INSERT OR IGNORE INTO Debil (NombreTipoDebil, NombreTipoFuerte) VALUES
('agua', 'planta'),
('hada', 'veneno');


-- ==========================================================
-- 5) POKEMON (tabla Pokemon con stats) para /stats y /compare
-- ==========================================================
-- Insertar Pokémon con estadísticas asociadas a su especie (IDEspecie = PokedexID).
-- (IDPokemon AUTOINCREMENT) -> se deja que la BD lo genere.
INSERT OR IGNORE INTO Pokemon
(Nombre, Nivel, PS, Ataque, AtaqueEspecial, Defensa, DefensaEspecial, Velocidad, IDEspecie)
VALUES
('bulbasaur', 5, 45, 49,  65, 49, 65, 45,  1),
('pikachu',   5, 35, 55,  50, 40, 50, 90, 25),
('porygon-z', 5, 85, 80, 135, 70, 75, 90, 474);


-- ==========================================================
-- 6) EQUIPO DEMO + RELACIÓN EQUIPO-POKEMON (para /score_team)
-- ==========================================================
-- Equipo del usuario admin.
INSERT OR IGNORE INTO Equipo (IDEquipo, Nombre, IDUsuario)
VALUES (1, 'EquipoDemo', 1);

-- Asociar 3 Pokémon al equipo en 3 slots.
-- Se resuelve el IDPokemon mediante SELECT para evitar depender de IDs fijos.
INSERT OR IGNORE INTO REquipoPokemon (IDEquipo, IDPokemon, Slot)
SELECT 1, p.IDPokemon, 1 FROM Pokemon p WHERE p.Nombre='bulbasaur';

INSERT OR IGNORE INTO REquipoPokemon (IDEquipo, IDPokemon, Slot)
SELECT 1, p.IDPokemon, 2 FROM Pokemon p WHERE p.Nombre='pikachu';

INSERT OR IGNORE INTO REquipoPokemon (IDEquipo, IDPokemon, Slot)
SELECT 1, p.IDPokemon, 3 FROM Pokemon p WHERE p.Nombre='porygon-z';
