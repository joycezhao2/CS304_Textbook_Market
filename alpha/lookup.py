import dbi

'''Returns a database connection for that db'''
def getConn(db):
    dsn = dbi.read_cnf("~/.textbook.cnf")
    # dsn = dbi.read_cnf()
    conn = dbi.connect(dsn)
    dbi.select_db(conn,db)
    return conn

def getPic(bid):
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    numrows = curs.execute(
        '''select pic from books where id = %s''',
        [bid])
    filename = curs.fetchone()

    return filename

def searchBook(search_term):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from books 
                    where title like %s
                    and sold_status = 0''',
            ['%'+search_term+'%'])

    return curs.fetchall()

def filterBook(dept, order):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    # finds the books with the criterias
    if order == '':
        curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0''',
                        [dept])
        return curs.fetchall()
    elif order == "price up":
        curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0
                        order by price asc''',
                        [dept])
        return curs.fetchall()
    elif order == "price down":
        curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0
                        order by price desc''',
                        [dept])
        return curs.fetchall()
    elif order == "newest":
        curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0
                        order by id desc''',
                        [dept])
        return curs.fetchall()
    elif order == 'condition':
        curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0
                        order by `condition` desc''',
                        [dept])
        return curs.fetchall()

def getAllDepts():
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    # gets all unique value of departments
    curs.execute('''select distinct department from courses''')
    return curs.fetchall()

def getSellingDepts():
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    # gets all unique value of departments
    curs.execute('''select distinct department
                    from courses
                    inner join books
                    where (courses.id = books.course)
                    and books.sold_status = 0''')
    return curs.fetchall()

def getSellingNums():
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    # gets all unique value of course numbers
    curs.execute('''select distinct number
                    from courses
                    inner join books
                    where (courses.id = books.course)
                    and books.sold_status = 0''')
    return curs.fetchall()

def getAllNums():
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    # gets all unique value of course numbers
    curs.execute('''select distinct number from courses 
                    order by number asc''')
    return curs.fetchall()

def getCourseNumbers(dept):
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    # finds all course numbers in the selected department
    curs.execute('''select distinct number from courses
                    where department = %s''',
                    [dept])
    return curs.fetchall()

def uploadBook(dept, course_num, price, condition, title, author, description, seller, filename):
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    # finds the course the book is for
    curs.execute('''select id from courses 
                    where department = %s
                    and number = %s''',
                    [dept, course_num])

    course_id = curs.fetchone()

    # insert the book into the database
    curs.execute('''insert into books(price, 
                                        sold_status,
                                        `condition`, 
                                        title, 
                                        author,
                                        `description`,
                                        seller,
                                        course,
                                        pic)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                    [price, 0, condition, title, author, description, seller, course_id, filename])

def findBook(book_id):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from books where id=%s''',
            [book_id])

    return curs.fetchone()

def createUser(name, username):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''insert into users(username, name, email, phnum)
                    values(%s, %s, %s, %s)''',
                    [username, name, username+'@wellesley.edu', None])

def searchUser(username):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from users where username=%s''',
            [username])

    return curs.fetchone()

def findBooksBySeller(username):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from books where seller=%s''',
            [username])

    return curs.fetchall()

def setSoldStatus(book_id, status):
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    if status == '1':
        curs.execute('''UPDATE books SET sold_status = 1 WHERE id=%s''',
            [book_id])
        return 1
    else: 
        curs.execute('''UPDATE books SET sold_status = 0 WHERE id=%s''',
            [book_id])
        return 0

def getCourseByID(cid):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select department, number 
                    from courses where id=%s''',
                    [cid])

    return curs.fetchone()
