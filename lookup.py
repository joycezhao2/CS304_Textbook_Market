import dbi

'''Returns a database connection for that db'''
def getConn(db):
    dsn = dbi.read_cnf()
    conn = dbi.connect(dsn)
    dbi.select_db(conn,db)
    return conn

# Makes the database connection available globally
CONN = getConn('textbooks_db')

def uploadBook(title, dept, course_num, prof, price, condition, description):
    curs = dbi.cursor(conn)

    curs.execute('''select id from courses 
                    where department = %s
                    and number = %s
                    and professor = %s''',
                    [dept, course_num, prof])
    course_id = curs.fetchone()

    curs.execute('''select book_id from A_book_course where
                    course_id = %s''',
                    [course_id])

    book_id = curs.fetchone()

    curs.execute('''insert into S_books(price, 
                                        sold_status,
                                        `condition`, 
                                        title, 
                                        description,
                                        seller,
                                        buyer, 
                                        book
                                        )
                    values (%s,%s,%s,%s,%s,%s,%s,%s)''',
                    [price, 0, condition, title, description, 'jzhao2', None, book_id])

    