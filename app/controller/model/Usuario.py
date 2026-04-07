class Usuario:
    def __init__(self, pIDUsuario, pNombre, pEmail, pContrasena, pEstado='Espera', pFavorito="Bulbasaur"):
        # Inicializa un usuario con ID, nombre, email, contraseña, estado y Pokémon favorito
        self.IDUsuario = pIDUsuario
        self.Nombre = pNombre
        self.Email = pEmail
        self.Contrasena = pContrasena
        self.Estado = pEstado
        self.Favorito = pFavorito
        
    def getData(self):
        # Devuelve los datos del usuario en un diccionario
        return {
            "IDUsuario": self.IDUsuario,
            "Nombre": self.Nombre,
            "Email": self.Email,
            "Contrasena": self.Contrasena,
            "Estado": self.Estado,
            "Favorito": self.Favorito
        }
    
    def editUser(self, pEmail, pContraseña, pNombrePKFav, pEstado):
        # Actualiza los atributos del usuario si se proporcionan nuevos valores
        if pEmail != '' and pEmail is not None:
            self.Email = pEmail
        if pContraseña != '' and pContraseña is not None:
            self.Contrasena = pContraseña
        if pNombrePKFav != '' and pNombrePKFav  is not None:
            self.Favorito = pNombrePKFav
        if pEstado != '' and pEstado is not None:
            self.Estado = pEstado

