from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
from werkzeug import secure_filename
app = Flask(__name__)

import random
import lookup

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

''' Route to handle the main search page. 
    When there is no search term, show all the movies '''
@app.route('/',  defaults={'term': ''})
@app.route('/search/<term>', methods=["GET"])
def index(term):
    books = lookup.searchBook(term)
    return render_template('main.html',title='Hello', books=books)

''' Route to handle searching for a book'''
@app.route('/searchBook/', methods=["POST"])
def searchBook():
    search_term = request.form.get("keyword")
    return redirect(url_for('index', term=search_term))

''' Route to handle uploading a book'''
@app.route('/submit/', methods=['GET', 'POST'])
def submit():
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

    return render_template('submit.html', title='Upload')

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
    cart = session.get('cart',{}) 
    
    if request.method == 'GET':
        book_info = []

        for book_id in cart.keys():
            book = lookup.findBook(book_id)
            book_info.append(book)
        return render_template('cart.html', title='Cart', cart=book_info)

    elif request.method == 'POST':
        # removing from cart
        item = request.form.get('bookid')
        cart.pop(item)
        session['cart'] = cart
        return redirect(url_for('session_cart'))

''' Route to display a book '''
@app.route('/book/<id>/')
def book(id):
    book = lookup.findBook(id)
    seller = lookup.searchUser(book['seller'])
    return render_template('book.html', 
                            title='Book',
                            book=book, 
                            seller=seller)

''' Route to display a user '''
@app.route('/users/<username>/')
def user(username):
    user = lookup.searchUser(username)
    selling = lookup.findBooksBySeller(username)
    return render_template('users.html', 
                            title='User',
                            user=user, 
                            selling=selling)  

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
