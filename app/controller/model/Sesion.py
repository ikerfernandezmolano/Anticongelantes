from app.controller.model.Usuario import Usuario  # importa tu clase Usuario

class Sesion:
    _instance = None

    def __new__(cls):
        # Implementa el patrón singleton para la sesión
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.usuario = Usuario(0,'','','','',0)  # Inicializa un usuario vacío
        return cls._instance

    def startSession(self, pIDUsuario, pNombre, pEmail, pContraseña, pAREA='Espera'):
        # Inicia sesión creando un usuario con los datos proporcionados
        self.usuario = Usuario(
            pIDUsuario=pIDUsuario,
            pNombre=pNombre,
            pEmail=pEmail,
            pContrasena=pContraseña,
            pEstado=pAREA
        )

    def cerrarSesion(self):
        # Cierra la sesión eliminando el usuario
        self.usuario = None
    
    def getSession(self):
        # Devuelve los datos del usuario en sesión
        return self.usuario.getData()
        
    def editSession(self, pEmail, pContraseña, pNombrePKFav, pEstado):
        # Edita los datos del usuario en sesión
        self.usuario.editUser(pEmail, pContraseña, pNombrePKFav, pEstado)
