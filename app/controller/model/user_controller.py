class UserController:

    def __init__(self, db):
        self.db = db

    def create_user(self, name):
        if not name or len(name.strip()) < 3:
            raise ValueError('El nombre debe tener al menos 3 caracteres.')

        self.db.insert(
            sentence="INSERT INTO users (name) VALUES (?)",
            parameters=[name.strip()]
        )

    def get_all(self):
        rows = self.db.select(
            sentence="SELECT * FROM users"
        )

        return [ dict(row) for row in rows ]