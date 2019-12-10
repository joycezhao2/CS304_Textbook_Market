import dbi

# Returns a database connection for that db
def getConn(db):
    # this line is to allow db connection on a personal account
    # dsn = dbi.read_cnf("~/.textbook.cnf")
    dsn = dbi.read_cnf()
    conn = dbi.connect(dsn)
    dbi.select_db(conn,db)
    return conn

# Returns the picture attached to a specified book
def getPic(bid):
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    numrows = curs.execute(
        '''select pic from books where id = %s''',
        [bid])
    filename = curs.fetchone()
    return filename

# Returns all books with a search term
def searchBook(search_term):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from books 
                    where title like %s
                    and sold_status = 0''',
                ['%'+search_term+'%'])
    return curs.fetchall()

# Returns the books with given criterias (department, course number, sorting order)
def filterBook(dept, num, order):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    # num == 0 handles the ajax version
    if order == '':
        if num == 0:
            curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0''',
                        [dept])
            return curs.fetchall()
        else:
            curs.execute('''select * from books
                            where course in
                            (select id from courses
                            where department = %s
                            and number = %s)
                            and sold_status = 0''',
                            [dept,num])
            return curs.fetchall()
    elif order == "price up":
        if num == 0:
            curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0
                        order by price asc''',
                        [dept])
            return curs.fetchall()
        else:
            curs.execute('''select * from books
                            where course in
                            (select id from courses
                            where department = %s
                            and number = %s)
                            and sold_status = 0
                            order by price asc''',
                            [dept,num])
            return curs.fetchall()
    elif order == "price down":
        if num == 0:
            curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0
                        order by price desc''',
                        [dept])
            return curs.fetchall()
        else:
            curs.execute('''select * from books
                            where course in
                            (select id from courses
                            where department = %s
                            and number = %s)
                            and sold_status = 0
                            order by price desc''',
                            [dept,num])
            return curs.fetchall()
    elif order == "newest":
        if num == 0:
            curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0
                        order by id desc''',
                        [dept])
            return curs.fetchall()
        else:
            curs.execute('''select * from books
                            where course in
                            (select id from courses
                            where department = %s
                            and number = %s)
                            and sold_status = 0
                            order by id desc''',
                            [dept,num])
            return curs.fetchall()
    elif order == 'condition':
        if num == 0:
            curs.execute('''select * from books
                        where course in
                        (select id from courses
                        where department = %s)
                        and sold_status = 0
                        order by `condition` desc''',
                        [dept])
            return curs.fetchall()
        else:
            curs.execute('''select * from books
                            where course in
                            (select id from courses
                            where department = %s
                            and number = %s)
                            and sold_status = 0
                            order by `condition` desc''',
                            [dept,num])
            return curs.fetchall()
            
# Returns all existing departments in the database
def getAllDepts():
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    curs.execute('''select distinct department from courses''')
    return curs.fetchall()

# Returns all existing course number in the database
def getAllNums():
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    curs.execute('''select distinct number from courses 
                    order by number asc''')
    return curs.fetchall()

# Returns all existing departments that some user is selling a book for
def getSellingDepts():
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    curs.execute('''select distinct department
                    from courses
                    inner join books
                    where (courses.id = books.course)
                    and books.sold_status = 0''')
    return curs.fetchall()

# Returns all existing course numbers that some user is selling a book for
def getSellingNums():
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    curs.execute('''select distinct number
                    from courses
                    inner join books
                    where (courses.id = books.course)
                    and books.sold_status = 0''')
    return curs.fetchall()

# Returns all course numbers associated with a given department
def getCourseNumbers(dept):
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)

    curs.execute('''select distinct number from courses
                    where department = %s''',
                    [dept])
    return curs.fetchall()

# Executes the upload of a book, returns whether insertion is successful 
def uploadBook(dept, course_num, price, condition, title, author, description, seller, filename):
    CONN = getConn('textbooks_db')
    curs = dbi.cursor(CONN)
    success = 1

    # finds the course the book is for
    curs.execute('''select id from courses 
                    where department = %s
                    and number = %s''',
                    [dept, course_num])
    course_id = curs.fetchone()
    if course_id is None:
        # if the user is trying to submit for an non-existing course
        return course_id
    else:
        # insert the book into the database
        curs.execute('''insert into books(price, sold_status,`condition`, title, author,
                                        `description`,seller,course,pic)
                        values (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                        [price, 0, condition, title, author, description, seller, course_id, filename])
        return 1

# Returns all information of a specific book
def findBook(book_id):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from books where id=%s''',
            [book_id])
    return curs.fetchone()

# Creates a new user in the database
def createUser(name, username):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''insert into users(username, name, email, phnum)
                    values(%s, %s, %s, %s)''',
                    [username, name, username+'@wellesley.edu', None])

# Returns the user with a given username
def searchUser(username):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from users where username=%s''',
            [username])
    return curs.fetchone()

# Returns all books a user is selling
def findBooksBySeller(username):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select * from books where seller=%s''',
            [username])
    return curs.fetchall()

# Updates the sold status of a given book
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

# Returns the course matching the specific course id
def getCourseByID(cid):
    CONN = getConn('textbooks_db')
    curs = dbi.dictCursor(CONN)

    curs.execute('''select department, number 
                    from courses where id=%s''',
                    [cid])
    return curs.fetchone()
