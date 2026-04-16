from app.controller.model.Sesion import Sesion

class GestorUsuarios:

    def __init__(self, db):
        # Inicializa el gestor con la base de datos
        self.db = db
        
#-----------------------AÑADIR/ELIMINAR USUARIO-----------------------------#

    def añadirUsuario(self, pUser, pEmail, pPasswd):
        # Añade un usuario a la base de datos y devuelve código de estado
        try:
            self.db.executeSQL(
                sql="INSERT INTO Usuario (Nombre, Email, Contrasena,Estado) VALUES (?,?,?,?)",
                parameters=[pUser.strip(),pEmail.strip(),pPasswd.strip(),"Espera"]
            )
            return 0
        except Exception as e:
            msg = str(e)

            if "Usuario.Nombre" in msg:
                return 1  # nombre repetido
            elif "Usuario.Email" in msg:
                return 2  # email repetido
            else:
                return 3  # otro error de integridad
                
    def borrarUsuario(self, idUser):
        # Borra un usuario a la base de datos
        self.db.executeSQL(sql="DELETE FROM Usuarios WHERE IDUsuario=?",
        parameters=[idUser]
        )
                
#-----------------------------INICIAR SESIÓN----------------------------------#
        
    def iniciarSesion(self, pEmail, pPasswd):
        # Inicia sesión validando email, contraseña y estado del usuario
        rows = self.db.execSQL(
            sql="SELECT * FROM Usuario WHERE Email=? LIMIT 1",
            parameters=[pEmail.strip()]
        )

        if not rows:
            # Usuario no encontrado
            return 1

        usuario = rows[0]  # tomamos la primera fila

        if pPasswd.strip() != usuario['Contrasena']:
            # Contraseña incorrecta
            return 2
            
        if usuario['Estado'] != 'Aceptado' and usuario['Estado'] != 'Admin':
            return 3
        
        sesion = Sesion()
        sesion.startSession(
            pIDUsuario=usuario['IDUsuario'],
            pNombre=usuario['Nombre'],
            pEmail=usuario['Email'],
            pContraseña=usuario['Contrasena'],
            pAREA=usuario['Estado']
        )
        return 0 # Estado correcto
        
#-----------------------------GETTERS INFO----------------------------------#
     
    def get_all(self):
        # Devuelve todos los usuarios
        rows = self.db.execSQL(
            sql="SELECT * FROM Usuario"
        )

        return [ dict(row) for row in rows ]
        
    def getSession(self):
        # Devuelve los datos de la sesión
        return Sesion().getSession()
        
    def get_usuario(self, user_id):
        # Devuelve los datos de un usuario
        rows = self.db.execSQL(
            sql="SELECT * FROM Usuario WHERE IDUsuario = ? LIMIT 1",
            parameters=[user_id]
        )
        
        return {
            "IDUsuario": rows[0]["IDUsuario"],
            "Nombre": rows[0]["Nombre"],
            "Email": rows[0]["Email"],
            "Estado": rows[0]["Estado"],
        }
        
#------------------------------MANAGE USERS-----------------------------------#
#-----------------------------GETTERS MANAGE----------------------------------#
        
    def get_aceptados(self):
        # Devuelve una lista con los usuarios aceptados
        rows = self.db.execSQL(
            sql="SELECT * FROM Usuario WHERE Estado = 'Aceptado'"
        )

        return [ dict(row) for row in rows ]
        
    def get_espera(self):
        # Devuelve una lista con los usuarios tanto rechazados, como en espera
        rows = self.db.execSQL(
            sql="SELECT * FROM Usuario WHERE Estado = 'Espera' OR Estado = 'Rechazado'"
        )

        return [ dict(row) for row in rows ]
        
#-----------------------------BOTONES MANAGE----------------------------------#
        
    def aceptar(self, user_id):
        # Cambia el estado del usuario a Aceptado
        self.db.executeSQL(
            sql="UPDATE Usuario SET Estado = 'Aceptado' WHERE IDUsuario = ?",
            parameters=[user_id]
        )
        
    def rechazar(self, user_id):
        # Cambia el estado del usuario a Rechazado
        self.db.executeSQL(
            sql="UPDATE Usuario SET Estado = 'Rechazado' WHERE IDUsuario = ?",
            parameters=[user_id]
        )
    
    def eliminar(self, user_id):
        # Elimina al usuario de la base de datos
        self.db.executeSQL(
            sql="DELETE FROM Usuario WHERE IDUsuario = ?",
            parameters=[user_id]
        )
        
#-----------------------------MODIFICAR DATOS----------------------------------#
        
    def modificarDatos(self, email, password_old, password_new):
        # A partir de los datos de la sesión almacenados y los nuevos datos, modifica la información almacenada del usuario de la sesión
        sesion = Sesion().getSession()

        # --- CONTRASEÑA ---
        if password_new.strip():
            if not password_old:
                return 3
            else:
                if password_old.strip() != sesion['Contrasena'].strip():
                    return 1
        else:
            password_new = sesion['Contrasena']
            
        
        # --- UPDATE ---
        try:
            self.db.executeSQL(
                sql="UPDATE Usuario SET Email=?, Contrasena=? WHERE IDUsuario=?",
                parameters=[email, password_new, sesion['IDUsuario']]
            )

            Sesion().editSession(
                pEmail=email,
                pContraseña=password_new,
                pEstado=''
            )
            return 0

        except Exception as e:
            if "Usuario.Email" in str(e):
                return 2  # email repetido
            return str(e)
            
#--------------------------MODIFICAR DATOS ADMIN-------------------------------#
        
    def modificarDatosAdmin(self, email, password, pkFav=None, user_id=1):
        # A partir de los datos del usuario pasado por parámetro almacenados y los nuevos datos, modifica la información almacenada del usuario
        sesion = Sesion().getSession()
        usuario = self.get_usuario(user_id)
        if sesion['Estado'] == 'Admin':
            if not password:
                password = usuario['Contrasena']
                
            # --- UPDATE ---
            try:
                self.db.executeSQL(
                    sql="UPDATE Usuario SET Email=?, Contrasena=? WHERE IDUsuario=?",
                    parameters=[email, password, user_id]
                )
                return 0

            except Exception as e:
                if "Usuario.Email" in str(e):
                    return 1  # email repetido
                return str(e)
        else:
            return 2
        
        
        
