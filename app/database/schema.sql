
CREATE TABLE IF NOT EXISTS Usuario (
    IDUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL UNIQUE,
    Email TEXT NOT NULL UNIQUE,
    Contrasena TEXT NOT NULL,
    Estado TEXT NOT NULL DEFAULT 'Espera'
);

CREATE TABLE IF NOT EXISTS Coche (
    idCoche INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    precio REAL NOT NULL,
    kilometraje INTEGER,
    imagen TEXT DEFAULT 'fondo.jpg'
);

INSERT OR IGNORE INTO Coche (idCoche, marca, modelo, precio, kilometraje, imagen) VALUES
(1, 'Ferrari', '458 Italia', 215000, 12000, 'ferrari.png'),
(2, 'Lamborghini', 'Huracán', 245000, 5000, 'Lamborghini.png'),
(3, 'Porsche', '911 Carrera', 115000, 30000, 'porsche.png'),
(4, 'Audi', 'R8 V10 Performance', 165000, 15000, 'audi.png'),
(5, 'Mercedes', 'AMG GT S', 130000, 22000, 'mercedes.png');

-- Inserción de usuario admin
INSERT OR IGNORE INTO Usuario (IDUsuario, Nombre, Email, Contrasena, Estado)
VALUES (1, 'admin', 'admin@admin.com', 'admin', 'Admin');
