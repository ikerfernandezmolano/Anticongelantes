from app.controller.model.book_controller import BookController


class LoanController:
    MAX_ACTIVE_LOANS = 3
    LOAN_DAYS = 14

    def __init__(self, db):
        self.db = db
        self.book_controller = BookController(db)

    def create_loan(self, user_id, book_id):

        rows = dict(
            self.db.select(
                sentence="""SELECT COUNT(*) AS total 
                            FROM loans 
                            WHERE user_id = ? AND status = 'ACTIVE'""",
                parameters=[user_id]
            )[0]
        )

        if int(rows['total']) >= self.MAX_ACTIVE_LOANS:
            raise ValueError("El usuario ha alcanzado el máximo de préstamos")

        has_stock = self.book_controller.has_stock(book_id)

        if not has_stock:
            raise ValueError("No hay copias disponibles de este libro")


        self.db.insert(
            sentence="INSERT INTO loans (user_id, book_id, status) VALUES (?, ?, ?)",
            parameters=[user_id, book_id, 'ACTIVE']
        )

    def return_loan(self, loan_id):
        rows = self.db.select(
            sentence="SELECT status FROM loans WHERE id = ?",
            parameters=[loan_id]
        )

        if not rows:
            raise ValueError("El préstamo no existe")

        rows = dict(rows[0])

        if rows['status'] != 'ACTIVE':
            raise ValueError("El préstamo ya ha sido devuelto")

        self.db.update(
            sentence="UPDATE loans SET status = ? WHERE id = ?",
            parameters=['RETURNED', loan_id],
        )


    def get_all(self):
        rows = self.db.select(
            sentence="""SELECT loans.id, users.name, books.title ,loans.status
                        FROM loans 
                        JOIN users ON users.id = loans.user_id 
                        JOIN books ON books.id = loans.book_id"""
        )

        return [ dict(row) for row in rows ]

    def get_active(self):
        rows = self.db.select(
            sentence="""
                     SELECT loans.id, users.name, books.title ,loans.status
                     FROM loans
                     JOIN users ON users.id = loans.user_id
                     JOIN books ON books.id = loans.book_id
                     WHERE loans.status = 'ACTIVE'
                     """,
        )

        return [ dict(row) for row in rows ]