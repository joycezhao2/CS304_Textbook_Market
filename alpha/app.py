from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
from werkzeug import secure_filename
app = Flask(__name__)

import random
import lookup
from flask_cas import CAS

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
app.config['CAS_AFTER_LOGIN'] = 'search'

@app.route('/')
def index():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
        return redirect(url_for('search'))
    return render_template('login.html')

''' Route to handle the main search page. 
    When there is no search term, show all the movies '''
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
    
    dept = request.form.get('dept')
    course_num = request.form.get('num')
    books = lookup.filterBook(dept,course_num)
    return render_template('main.html',
                            title='Hello',
                            books=books,
                            username=username)


''' Route to handle uploading a book'''
@app.route('/submit/', methods=['GET', 'POST'])
def submit():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title')
        dept = request.form.get('department')
        course_num = request.form.get('number')
        prof = request.form.get('prof')
        price = request.form.get('price')
        condition = request.form.get('condition')
        description = request.form.get('description')

        # insert into db
        lookup.uploadBook(dept, course_num, 
                            prof, price, condition, title, description)

        flash('Upload successful')

    return render_template('submit.html', title='Upload', username=username)

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
    seller = lookup.searchUser(book['seller'])
    return render_template('book.html', 
                            title='Book',
                            book=book, 
                            seller=seller,
                            username=username)

''' Route to display a user '''
@app.route('/users/<username>/')
def user(username):
    if 'CAS_USERNAME' in session:
        loggedIn = session['CAS_USERNAME']
    else:
        return redirect(url_for('index'))

    user = lookup.searchUser(username)
    selling = lookup.findBooksBySeller(username)
    return render_template('users.html', 
                            title='User',
                            user=user, 
                            selling=selling,
                            username=loggedIn)  

''' Route to display handle the buttons in the search page '''
@app.route('/bookreq/', methods=["POST"])
def bookreq():
    submit = request.form.get("submit")
    if submit == "Book Information":
        bid = request.form.get("bookid")
        return redirect(url_for('book',id=bid))
    elif submit == "Seller Information":
        uid = request.form.get("uid")
        return redirect(url_for('user', username='jzhao2'))
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
