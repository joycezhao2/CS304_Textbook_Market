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
# end of mail stuff;

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

@app.route('/')
def index():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
        return redirect(url_for('search'))
    return render_template('login.html')

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
    When there is no search term, show all the books for sale '''
@app.route('/search/',  defaults={'term': ''})
@app.route('/search/<term>', methods=["GET"])
def search(term):
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    books = lookup.searchBook(term)

    return render_template('main.html',
                            title='Hello',
                            books=books,
                            username=username)

''' Route to handle searching for a book'''
@app.route('/searchBook/', methods=["POST"])
def searchBook():
    search_term = request.form.get("keyword")
    return redirect(url_for('index', term=search_term))

@app.route('/filterBook/', methods=["GET"])
def filterBook():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))
    
    try: 
        dept = request.args.get('dept')
        course_num = request.args.get('num')
        order = request.args.get('sort')

        books = lookup.filterBook(dept,course_num,order)
        return render_template('main.html',
                                title='Hello',
                                books=books,
                                username=username)
    except Exception as err:
        flash('form submission error' + str(err))
        return redirect(url_for('index'))

# @app.route('/filterBookAjax/', methods=['POST'])
# def filterBookAjax():
#     if 'CAS_USERNAME' in session:
#         username = session['CAS_USERNAME']
#     else:
#         return redirect(url_for('index'))

#     dept = request.form['dept']
#     course_nums = request.form['nums']
#     if len(course_nums) == 1:
#         books = lookup.filterBook(dept,course_nums)
#         try:
#             return jsonify({'error':False, 
#                             'dept':dept, 
#                             'nums':course_nums,
#                             'books':books})
#         except Exception as err:
#             print(err)
#             return jsonify({'error':True, 'err':str(err)})
#     else course_nums == 0:
#         courses = lookup.getCourseNumbers(dept)
#         # books = lookup.getDeptBooks(dept)
#         try:
#             return jsonify({'error':False,
#                             'dept':dept,
#                             'nums':courses)
#         except Exception as err:
#             print(err)
#             return jsonify({'error':True, 'err':str(err)})

''' Route to handle uploading a book'''
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
        dept = request.form.get('department')
        course_num = request.form.get('number')
        price = request.form.get('price')
        condition = request.form.get('condition')
        description = request.form.get('description')

        # handling pictures
        pic = request.files['pic']
        user_filename = pic.filename
        ext = user_filename.split('.')[-1]
        filename = secure_filename('{}-{}.{}'.format(username,title,ext))
        pathname = os.path.join(app.config['UPLOADS'],filename)
        pic.save(pathname)

        # insert into db
        lookup.uploadBook(dept, course_num, price, condition, title, author, 
                            description, username, filename)

        flash('Upload successful')

    return render_template('submit.html',
                            title='Upload',
                            username=username,
                            depts=departments,
                            cnums=course_nums)

''' Route to handle adding to your cart (session based)'''
@app.route('/addCart/', methods=["POST"])
def addCart():
    cart = session.get('cart', {}) 
    book = request.form.get('bookid')

    # use dict to prevent repitition of same book
    cart[book] = 1
    session['cart'] = cart
    flash('Book added to cart successfully')
    return redirect(request.referrer)

''' Route to handle showing your cart and deleting from it'''
@app.route('/session/cart/', methods=['GET','POST'])
def session_cart():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    cart = session.get('cart',{}) 
    
    if request.method == 'GET':
        book_info = []

        for book_id in cart.keys():
            book = lookup.findBook(book_id)
            book_info.append(book)
        return render_template('cart.html', 
                                title='Cart',
                                cart=book_info,
                                username=username)

    elif request.method == 'POST':
        # removing from cart
        item = request.form.get('bookid')
        cart.pop(item)
        session['cart'] = cart
        return redirect(url_for('session_cart'))

''' Route to display a book '''
@app.route('/book/<id>/')
def book(id):
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    book = lookup.findBook(id) 

    return render_template('book.html', 
                            title='Book',
                            book=book, 
                            seller=book['seller'],
                            email=book['seller']+'@wellesley.edu',
                            username=username)

''' Route to display a user '''
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
                            name=user['name'], 
                            selling=selling,
                            username=username,
                            loggedInUser=loggedInUser)  

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
            msg = Message(subject=subject,
                          sender=sender,
                          recipients=[recipient],
                          body=body)
            mail.send(msg)
            flash('email sent successfully')
            return redirect(request.referrer)

        except Exception as err:
            print(['err',err])
            flash('form submission error'+str(err))
            return redirect(request.referrer)

''' Route to display handle the buttons in the search page '''
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
