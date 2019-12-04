import dbi

'''Returns a database connection for that db'''
def getConn(db):
    # dsn = dbi. read_cnf("~/.textbook.cnf")
    dsn = dbi.read_cnf()
    conn = dbi.connect(dsn)
    dbi.select_db(conn,db)
    return conn

# Makes the database connection available globally
CONN = getConn('textbooks_db')

def searchBook(search_term):
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from S_books where title like %s''',
            ['%'+search_term+'%'])

    return curs.fetchall()

def uploadBook(dept, course_num, prof, price, condition, title, description):
    curs = dbi.cursor(CONN)

    # finds the course the book is for
    curs.execute('''select id from courses 
                    where department = %s
                    and number = %s
                    and professor = %s''',
                    [dept, course_num, prof])
    course_id = curs.fetchone()

    # finds the A_book the book is for
    if course_id: 
        curs.execute('''select book_id from A_book_course where
                    course_id = %s''',
                    [course_id[0]])
        book_id = curs.fetchone()
    else: 
        book_id = 1

    # insert the S_book into the database
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

def findBook(book_id):
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from S_books where id=%s''',
            [book_id])

    return curs.fetchone()

def searchUser(username):
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from users where username=%s''',
            [username])

    return curs.fetchone()

def findBooksBySeller(username):
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from S_books where seller=%s''',
            [username])

    return curs.fetchall()