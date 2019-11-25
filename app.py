from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
from werkzeug import secure_filename
app = Flask(__name__)

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('main.html',title='Hello')

@app.route('/submit/')
def submit():
    print(session.get('cart', {}))

    return render_template('testform.html')

@app.route('/addCart/', methods=["POST"])
def addCart():
    cart = session.get('cart', {}) 
    book = request.form.get('bookid')

    # use dict to prevent repitition of same book
    cart[book] = 1
    session['cart'] = cart
    flash('Book added to cart successfully')

    return redirect(request.referrer)

@app.route('/session/cart/', methods=['GET','POST'])
def session_cart():
    cart = session.get('cart',{}) 
    if request.method == 'GET':
        return render_template('cart.html', cart=cart)
    elif request.method == 'POST':
        # removing from cart
        item = request.form.get('bookid')
        cart.pop(item)
        session['cart'] = cart
        return render_template('cart.html', cart=cart)

@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html', title='Customized Greeting')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.form)
    else:
        return render_template('form_data.html',
                               method=request.method,
                               form_data={})

@app.route('/testform/')
def testform():
    return render_template('testform.html')

@app.route('/book/<id>/')
def book(id):
    return render_template('book.html', id=id)

@app.route('/users/<username>/')
def user(username):
    selling=[123,234,345,456]
    return render_template('users.html', selling=selling)  

@app.route('/bookreq/', methods=["POST"])
def bookreq():
    submit = request.form.get("submit")
    if submit == "Book Information":
        bid = request.form.get("bookid")
        return redirect(url_for('book',id=bid))
    elif submit == "Seller Information":
        uid = request.form.get("uid")
        return redirect(url_for('user', username=123))
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
