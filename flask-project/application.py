import os

import sqlite3
from flask import Flask,render_template,request
from flask import send_from_directory
from flask import url_for
from werkzeug.utils import secure_filename, redirect

application = Flask(__name__)
import pymysql
db = pymysql.connect("flask-shopcart.cci1dwkfz7ga.us-west-2.rds.amazonaws.com", "shafali", "9417755499", "flaskdb")

application.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

loggedIn=True
firstName='Veronica'
email='xyz@gmail.com'


@application.route('/',methods=['GET', 'POST'])
def home():
    return render_template('home.html')
@application.route('/about/')
def about():
    return render_template('about.html')

@application.route('/search/',methods=['GET','POST'])
def search():
    return render_template('search.html')
@application.route('/login/',methods=['GET','POST'])
def login():
    return render_template('login.html')
@application.route('/register/',methods=['GET','POST'])
def register():
    return render_template('register.html')
@application.route("/")
def root():
    cur = db.cursor()
    cur.execute('SELECT productId, name, price, description, image, stock FROM products')
    itemData = cur.fetchall()
    cur.execute('SELECT categoryId, name FROM categories')
    categoryData = cur.fetchall()
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, categoryData=categoryData)
@application.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@application.route('/trendy_Tops')
def trendy_Tops():
    cur = db.cursor()
    cur.execute('SELECT productId, name, price, description, image, stock FROM products')
    itemData = cur.fetchall()
    itemData = parse(itemData)

    return render_template("trendy_Tops.html", image_names=itemData)


@application.route("/cart")
def cart():
    cur = db.cursor()
    cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
    userId = cur.fetchone()[0]
    cur.execute(
        "SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(
            userId))
    products = cur.fetchall()
    for elem in products:
        print(elem[1])



    totalPrice = 0
    for row in products:
        ship_price = row[2] + 10
        totalPrice += ship_price
        totalPrice = round(totalPrice, 4)
    return render_template("cart.html", products=products, totalPrice=totalPrice, loggedIn=loggedIn,
                           firstName=firstName)
@application.route("/addToCart")
def addToCart():
        productId = int(request.args.get('productId'))
        print(productId)
        cur = db.cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        print userId
        cur.execute("INSERT INTO kart (userId, productId) VALUES ("+str(userId)+", "+str(productId)+")")
        db.commit()

        return redirect(url_for('cart'))

@application.route("/removeFromCart")
def removeFromCart():
    productId = int(request.args.get('productId'))
    cur = db.cursor()
    cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
    userId = cur.fetchone()[0]
    cur.execute("DELETE FROM kart WHERE userId = " + str(userId) + " AND productId = " + str(productId))
    db.commit()

    return redirect(url_for('cart'))

class Products(object):
    ProductId = 0
    name= ""
    price = 0
    def __init__(self, ProductId, name, price):
        self.ProductId = ProductId
        self.name = name
        self.price = price


    def __repr__(self):
        return str({"ProductId":self.ProductId,"ProductName":self.name,"ProductPrice":self.price})


@application.route("/checkout")
def checkout():
    resp_list = []
    response_dict = {}
    import random
    import string
    paymentId = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    cur = db.cursor()
    cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
    userId = cur.fetchone()[0]
    cur.execute(
        "SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(
            userId))
    products = cur.fetchall()

    totalPrice = 0
    for row in products:
        ship_price = row[2] + 10
        totalPrice += ship_price
    for elem in products:
        t = Products(elem[0], elem[1], elem[2])
        resp_list.append(t)
    response_dict["Products"] = resp_list
    response_dict["totalPrice"] = totalPrice

    return render_template("checkout.html", response_dict=response_dict)





def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    application.run(debug=True)
