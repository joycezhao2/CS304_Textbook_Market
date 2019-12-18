from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify, Response)
from werkzeug import secure_filename
app = Flask(__name__)

import sys, os, random
import lookup
import imghdr
from flask_cas import CAS

from flask_mail import Mail, Message

app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='localhost',    # default; works on Tempest
    MAIL_PORT=25,               # default
    MAIL_USE_SSL=False,         # default
    MAIL_USERNAME='textbookmarket@wellesley.edu'
)
mail = Mail(app)

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'verify'
app.config['UPLOADS'] = 'pic'

''' The default main page'''
@app.route('/')
def index():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
        return redirect(url_for('search'))
    return render_template('login.html')

''' Route that checks if log-in information is correct'''
@app.route('/verify/', methods=["GET", "POST"])
def verify():
    username = session['CAS_USERNAME']
    user = lookup.searchUser(username)
    
    if request.method == 'GET':
        # if they've created an account before
        if user:
            return redirect(url_for('search'))

        # otherwise have them make an account
        return render_template('account.html')
    
    elif request.method == 'POST':
        name = request.form.get('name')
        lookup.createUser(name, username)
        return redirect(url_for('search'))

''' Route to handle the search page. 
    When there is no search term, show all the books for sale'''
@app.route('/search/',  defaults={'term': ''})
@app.route('/search/<term>', methods=["GET"])
def search(term):
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    books = lookup.searchBook(term)

    deptSold = lookup.getSellingDepts()
    numberSold = lookup.getSellingNums()

    return render_template('main.html',
                            title='Hello',
                            depts=deptSold,
                            nums=numberSold,
                            books=books,
                            loggedInUser=username)

''' Route to handle searching with a user input'''
@app.route('/searchBook/', methods=["POST"])
def searchBook():
    search_term = request.form.get("keyword")
    return redirect(url_for('search', term=search_term))

'''Route to handle filtering with selected criterias (department, course number, sorting order)'''
@app.route('/filter/', methods=["GET"])
def filter():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))
    
    try: 
        dept = request.args.get('department')
        num = request.args.get('course_number')
        order = request.args.get('sorting')

        books = lookup.filterBook(dept, num, order)
        
        deptSold = lookup.getSellingDepts()
        numberSold = lookup.getSellingNums()

        return render_template('main.html',
                                title='Hello',
                                loggedInUser=username,
                                depts=deptSold,
                                nums=numberSold,
                                books=books)
    except Exception as err:
        flash('form submission error' + str(err))
        return redirect(url_for('index'))

'''Route directing to the 'filter' route for searching'''
@app.route('/filterBook/', methods=["POST"])
def filterBook():
    dept = request.form.get('department')
    num = request.form.get('course_number')
    order = request.form.get('sorting')
    return redirect(url_for('filter', dept=dept, num=num, order=''))

'''Route handling ajax version of filtering books with criterias (department and sorting order)'''
@app.route('/filterBookAjax/',methods=["POST"])
def filterBookAjax():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    dept = request.form['dept']
    sort = request.form['sort']

    if dept:
        session['dept'] = dept
        session['sort'] = sort
    else:
        session['sort'] = sort
        deptSaved = session['dept']
        dept = deptSaved
    
    # Didn't implemented auto updates for course numbers in the drop-down list
    # Set num to 0 so that lookup.py can handle the Ajax case and the traditional route
    num = 0

    books = lookup.filterBook(dept,num,sort)
    for book in books:
        book['url'] = url_for("book",id=book['id'])

    try:
        return jsonify({'error':False, 'dept':dept, 'sort':sort,'books':books})
    except Exception as err:
        print(err)
        return jsonify({'error':True, 'err':str(err)})

'''Route handling submission page where available course number will show up given a selected department'''
@app.route('/uploadBookAjax/', methods=['POST'])
def uploadBookAjax():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    dept = request.form['dept']
    courses = lookup.getCourseNumbers(dept)
    try:
        return jsonify({'error':False, 
                        'dept':dept, 
                        'nums':courses})
    except Exception as err:
        print(err)
        return jsonify({'error':True, 'err':str(err)})

''' Route to handle uploading a book into the database'''
@app.route('/submit/', methods=['GET', 'POST'])
def submit():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    departments = lookup.getAllDepts()
    course_nums = lookup.getAllNums()

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        dept = request.form.get('departments')
        course_num = request.form.get('course_nums')
        price = request.form.get('price')
        condition = request.form.get('condition')
        description = request.form.get('description')
        professor = request.form.get('professor')
        year = request.form.get('year')

        # handling pictures
        pic = request.files['pic']
        if pic.filename == '': 
            filename = secure_filename('default-book.png')
            pathname = os.path.join(app.config['UPLOADS'],filename)
        else: 
            user_filename = pic.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}-{}.{}'.format(username,title,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            pic.save(pathname)

        # insert into db
        insert = lookup.uploadBook(dept, course_num, price, condition, title, author, 
                                    description, username, filename, professor, year)
        if insert == 1:
            flash('Upload successful')
        else:
            flash ("Course doesn't exist")
            return redirect(request.referrer)

    return render_template('submit.html',
                            title='Upload',
                            loggedInUser=username,
                            username=username,
                            depts=departments,
                            cnums=course_nums)

''' Route handling book pictures'''
@app.route('/bookPic/<bid>/')
def bookPic(bid):
    filename = lookup.getBookPic(bid)   
    return send_from_directory(app.config['UPLOADS'],filename[0])

''' Route handling user profile'''
@app.route('/profilePic/<username>/')
def profilePic(username):
    filename = lookup.getUserPic(username)   
    return send_from_directory(app.config['UPLOADS'],filename[0])

'''Route handling adding to your cart (session based)'''
@app.route('/addCart/', methods=["POST"])
def addCart():
    cart = session.get('cart', {}) 
    book = request.form.get('bookid')

    # use dict to prevent repitition of same book
    cart[book] = 1
    session['cart'] = cart
    flash('Book added to cart successfully')
    return redirect(request.referrer)

'''Route handling showing your cart and deleting from it'''
@app.route('/session/cart/', methods=['GET','POST'])
def session_cart():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    cart = session.get('cart',{}) 
    
    if request.method == 'GET':
        book_info = [lookup.findBook(book_id) for book_id in cart.keys()]        
        return render_template('cart.html', 
                                title='Cart',
                                loggedInUser=username,
                                cart=book_info,
                                username=username)
    elif request.method == 'POST':
        # removing from cart
        item = request.form.get('bookid')
        cart.pop(item)
        session['cart'] = cart
        return redirect(url_for('session_cart'))

'''Route to display a book'''
@app.route('/book/<id>/')
def book(id):
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    book = lookup.findBook(id) 

    c = book['condition']
    condition =''
    if c == '5':
        condition = 'Brand New' 
    elif c == '4':
        condition = 'Like New' 
    elif c == '3':
        condition = 'Very Good'
    elif c == '2':
        condition = 'Good'  
    elif c == '1':
        condition = 'Acceptable'

    course_id = book['course']
    related_course = lookup.getCourseByID(course_id)

    return render_template('book.html', 
                            title='Book',
                            loggedInUser=username,
                            book=book, 
                            course=related_course,
                            condition=condition,
                            seller=book['seller'],
                            email=book['seller']+'@wellesley.edu')

'''Route to display a user'''
@app.route('/users/<username>/')
def user(username):
    if 'CAS_USERNAME' in session:
        loggedInUser = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    selling = lookup.findBooksBySeller(username)
    user = lookup.searchUser(username)
    return render_template('users.html', 
                            title='User',
                            user=user, 
                            selling=selling,
                            username=username,
                            loggedInUser=loggedInUser)  

'''Route to edit user profile'''
@app.route('/editProfile/<username>/', methods=["GET", "POST"])
def editProfile(username):
    if 'CAS_USERNAME' in session:
        loggedInUser = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    selling = lookup.findBooksBySeller(username)
    user = lookup.searchUser(username)

    pic = request.files['profilepic']
    bio = request.form.get("userBio")
    
    # if a photo is uploaded, save it in the filesystem and 
    # update it in the database
    if pic.filename != '': 
        user_filename = pic.filename
        ext = user_filename.split('.')[-1]
        filename = secure_filename('{}.{}'.format(username,ext))
        pathname = os.path.join(app.config['UPLOADS'],filename)
        pic.save(pathname)
        lookup.uploadProfilePic(filename, username)
    
    # Update the bio
    lookup.updateBio(bio, username)
    flash('Profile updated')
    return redirect(url_for('user', username=username))

'''Route to send an email to a user'''
@app.route('/send_mail/', methods=["GET", "POST"])
def send_mail():
    if request.method == 'GET':
        return redirect(request.referrer)
    else:
        try:
             # throw error if there's trouble
            sender = session['CAS_USERNAME'] + "@wellesley.edu"
            recipient = request.form.get("userEmail")
            subject = request.form['subject']
            body = request.form['body']
            msg = Message(subject=subject, sender=sender, recipients=[recipient], body=body)
            mail.send(msg)
            flash('email sent successfully')
            return redirect(request.referrer)
        except Exception as err:
            print(['err',err])
            flash('form submission error'+str(err))
            return redirect(request.referrer)

''' Route handling the buttons displayed on the search page '''
@app.route('/bookreq/', methods=["POST"])
def bookreq():
    submit = request.form.get("submit")
    if submit == "Book Information":
        bid = request.form.get("bookid")
        return redirect(url_for('book',id=bid))
    elif submit == "Seller Information":
        uid = request.form.get("uid")
        return redirect(url_for('user', username=uid))
    elif submit == "Add to Cart":
        return redirect(url_for('addCart'),  code=307)
    else:
        return redirect("/")

'''Route handling "mark as sold" checkbox with Ajax'''
@app.route('/update_sold_status_ajax/', methods=["POST"])
def updateSoldStatusAjax():
    bid = request.form.get('id')
    status = request.form['sold_status']
    status = lookup.setSoldStatus(bid,status)
    return jsonify({'sold_status': status})

'''Route that handles updating book information'''
@app.route('/update/<id>', methods=["GET", "POST"])
def update(id):
    book = lookup.findBook(id)
    if request.method == "POST":
        bookAuthor = request.form.get('book-author')
        bookPrice = request.form.get('book-price')
        bookProfessor = request.form.get('book-professor')
        bookYear = request.form.get('book-year')
        
        #if update button is clicked
        if request.form['submit'] == 'update':
            lookup.update(bookAuthor, bookPrice, bookProfessor, bookYear, id)
            flash('Fields updated successfully')
    return redirect(request.referrer)

''' Route that deletes a book you're selling '''
@app.route('/delete/', methods=["POST"])
def delete():
    if 'CAS_USERNAME' in session:
        loggedInUser = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    bid = request.form.get('bookid')
    lookup.deleteBook(bid)
    flash ('Book was deleted')
    return redirect(url_for('user', username=loggedInUser))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
