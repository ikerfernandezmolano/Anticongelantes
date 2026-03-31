class BookController:

    def __init__(self, db):
        self.db = db

    def create_book(self, title, copies):
        if not title or copies<=0:
            raise ValueError("Datos inválidos")

        self.db.insert(
            sentence="INSERT INTO books (title, total_copies) VALUES (?, ?)",
            parameters=[title.strip(), copies]
        )

    def get_all(self):
        rows = self.db.select(
            sentence="""SELECT
                            books.id,
                            books.title,
                            books.total_copies,
                            books.total_copies - 
                            COUNT(loans.id) AS available_copies
                        FROM books
                        LEFT JOIN loans
                            ON books.id = loans.book_id
                            AND loans.status = 'ACTIVE'
                        GROUP BY books.id
                        ORDER BY books.title ASC"""
        )

        return [ dict(row) for row in rows ]

    def get_stock(self, book_id):
        rows = self.db.select(
            sentence="""SELECT
                            books.total_copies - 
                            COUNT(loans.id) AS available_copies
                        FROM books
                        LEFT JOIN loans
                            ON books.id = loans.book_id
                            AND loans.status = 'ACTIVE'
                        WHERE books.id = ?
                        GROUP BY books.id""",
            parameters=[book_id]
        )

        if not rows:
            raise ValueError("El libro no existe")

        return int(dict(rows[0])['available_copies'])

    def has_stock(self, book_id):
        stock = self.get_stock(book_id)
        return stock > 0
