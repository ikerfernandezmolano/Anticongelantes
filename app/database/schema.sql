
CREATE TABLE IF NOT EXISTS Usuario (
    IDUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL UNIQUE,
    Email TEXT NOT NULL UNIQUE,
    Contrasena TEXT NOT NULL,
    Estado TEXT NOT NULL DEFAULT 'Espera',
    IDFavorito INTEGER DEFAULT 1,
    FOREIGN KEY (IDFavorito) REFERENCES Especie(PokedexID)
);

-- Inserción de usuario admin
INSERT OR IGNORE INTO Usuario (IDUsuario, Nombre, Email, Contrasena, Estado, IDFavorito)
VALUES (1, 'admin', 'admin@admin.com', 'admin', 'Admin', 1);

CREATE TABLE IF NOT EXISTS Seguidor (
    IDUsuarioSeguido INTEGER,
    IDUsuarioSeguidor INTEGER,
    PRIMARY KEY (IDUsuarioSeguido, IDUsuarioSeguidor),
    FOREIGN KEY (IDUsuarioSeguido) REFERENCES Usuario(IDUsuario),
    FOREIGN KEY (IDUsuarioSeguidor) REFERENCES Usuario(IDUsuario)
);
CREATE TABLE IF NOT EXISTS Equipo (
    IDEquipo INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL,
    IDUsuario INTEGER NOT NULL,
    FOREIGN KEY (IDUsuario) REFERENCES Usuario(IDUsuario)
);

CREATE TABLE IF NOT EXISTS Especie (
    PokedexID INTEGER PRIMARY KEY,
    Nombre TEXT NOT NULL,
    EsLegendario INTEGER NOT NULL DEFAULT 0,
    Generacion INTEGER NOT NULL,
    Sprite TEXT NOT NULL DEFAULT 'None',
    NombreItem TEXT DEFAULT 'None',
    Descripcion TEXT DEFAULT 'None',
    Altura REAL,
    Peso REAL,
    Categoria TEXT,
    TieneEvolucion INTEGER,
    Prevolucion INTEGER,
    FOREIGN KEY (Prevolucion) REFERENCES Especie(PokedexID)
);

CREATE TABLE IF NOT EXISTS Pokemon (
    IDPokemon INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL,
    Nivel INTEGER,
    PS INTEGER,
    Ataque INTEGER,
    AtaqueEspecial INTEGER,
    Defensa INTEGER,
    DefensaEspecial INTEGER,
    Velocidad INTEGER,
    IDEspecie INTEGER NOT NULL,
    FOREIGN KEY (IDEspecie) REFERENCES Especie(PokedexID)
);



CREATE TABLE IF NOT EXISTS REquipoPokemon (
    IDEquipo INTEGER,
    IDPokemon INTEGER,
    Slot INTEGER,
    PRIMARY KEY (IDEquipo, IDPokemon),
    FOREIGN KEY (IDEquipo) REFERENCES Equipo(IDEquipo) ON DELETE CASCADE,
    FOREIGN KEY (IDPokemon) REFERENCES Pokemon(IDPokemon)
);
CREATE TABLE IF NOT EXISTS Captura (
    IDUsuario INTEGER,
    IDPokemonCapturado INTEGER,
    Fecha TEXT,
    PRIMARY KEY (IDUsuario, IDPokemonCapturado),
    FOREIGN KEY (IDUsuario) REFERENCES Usuario(IDUsuario),
    FOREIGN KEY (IDPokemonCapturado) REFERENCES Pokemon(IDPokemon)
);

CREATE TABLE IF NOT EXISTS Tipo (
    Nombre TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Debil (
    NombreTipoDebil TEXT,
    NombreTipoFuerte TEXT,
    PRIMARY KEY (NombreTipoDebil, NombreTipoFuerte),
    FOREIGN KEY (NombreTipoDebil) REFERENCES Tipo(Nombre),
    FOREIGN KEY (NombreTipoFuerte) REFERENCES Tipo(Nombre)
);

CREATE TABLE IF NOT EXISTS REspecieTipo (
    NombreTipo TEXT,
    PokedexID INTEGER,
    PRIMARY KEY (NombreTipo, PokedexID),
    FOREIGN KEY (NombreTipo) REFERENCES Tipo(Nombre),
    FOREIGN KEY (PokedexID) REFERENCES Especie(PokedexID)
);
CREATE TABLE IF NOT EXISTS Habilidad (
    IDHabilidad INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL,
    Descripcion TEXT
);
CREATE TABLE IF NOT EXISTS REspecieHabilidad (
    IDHabilidad INTEGER,
    PokedexID INTEGER,
    PRIMARY KEY (IDHabilidad, PokedexID),
    FOREIGN KEY (IDHabilidad) REFERENCES Habilidad(IDHabilidad),
    FOREIGN KEY (PokedexID) REFERENCES Especie(PokedexID)
);
CREATE TABLE IF NOT EXISTS Movimiento (
    IDMovimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    Nombre TEXT NOT NULL,
    NombreTipo TEXT,
    FOREIGN KEY (NombreTipo) REFERENCES Tipo(Nombre)
);
CREATE TABLE IF NOT EXISTS REspecieMovimiento (
    IDMovimiento INTEGER,
    PokedexID INTEGER,
    PRIMARY KEY (IDMovimiento, PokedexID),
    FOREIGN KEY (IDMovimiento) REFERENCES Movimiento(IDMovimiento),
    FOREIGN KEY (PokedexID) REFERENCES Especie(PokedexID)
);
CREATE TABLE IF NOT EXISTS Mensaje (
    Fecha TEXT,
    IDUsuario INTEGER,
    Texto TEXT,
    PRIMARY KEY (Fecha, IDUsuario),
    FOREIGN KEY (IDUsuario) REFERENCES Usuario(IDUsuario)
);
