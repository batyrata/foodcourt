from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, DecimalField, SelectField, FileField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import os
import re



app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'foodcourt'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#init MYSQL
mysql = MySQL(app)

#Appetizers = Appetizers()

#Check if the User is Logged In
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized user, please Login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Index Page
@app.route('/')
def index():
    return render_template("index.html")

#Charts Page
@app.route('/charts')
@is_logged_in
def charts():
    return render_template("charts.html")

#Appetizers Page
@app.route('/appetizers')
@is_logged_in
def appetizers():
    #Create a cursor
    cur = mysql.connection.cursor()

    #Get Appetizers
    result = cur.execute("SELECT * FROM appetizers ORDER BY name")

    appetizers = cur.fetchall()

    if result > 0:
        return render_template("appetizers.html", appetizers = appetizers)
    else:
        msg = "No Appetizers Found"
        return render_template("appetizers.html", msg=msg)

    #Close connection
    cur.close()


#Single Appetizer Page
@app.route('/appetizer/<string:id>/')
@is_logged_in
def appetizer(id):
    #Create a cursor
    cur = mysql.connection.cursor()

    #Get Appetizers
    result = cur.execute("SELECT * FROM appetizers WHERE id = %s", [id])

    appetizer = cur.fetchone()

    return render_template("appetizer.html", appetizer = appetizer)

#Class for Form Validation
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email',[validators.Length(min=6, max=50)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not Match!')
    ])
    confirm = PasswordField('Confirm Password')

#Main Dishes Page
@app.route('/main_dishes')
@is_logged_in
def main_dishes():
    #Create a cursor
    cur = mysql.connection.cursor()

    #Get Appetizers
    result = cur.execute("SELECT * FROM main_dishes ORDER BY name")

    main_dishes = cur.fetchall()

    if result > 0:
        return render_template("main_dishes.html", main_dishes = main_dishes)
    else:
        msg = "No Main Dishes are Found"
        return render_template("main_dishes.html", msg=msg)

    #Close connection
    cur.close()

#Single Main Dish Page
@app.route('/main_dish/<string:id>/')
@is_logged_in
def main_dish(id):
    #Create a cursor
    cur = mysql.connection.cursor()

    #Get Appetizers
    result = cur.execute("SELECT * FROM main_dishes WHERE id = %s", [id])

    main_dish = cur.fetchone()

    return render_template("main_dish.html", main_dish = main_dish)


#Register Page
@app.route('/register', methods=['GET','POST'])
@is_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Create Cursor
        cur = mysql.connection.cursor()

        x = cur.execute("SELECT * FROM users WHERE username = (%s)", [username])

        if x > 0:
            flash("That username already exists, please use another!")
            return render_template('register.html', form=form)

        else:
            #Execute query
            cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s, %s, %s, %s)", (name,email,username,password))

            #Commit to DB
            mysql.connection.commit()

            #Close the connection
            cur.close()
            flash('You are now registered and can log in', 'success')

            return redirect(url_for('login'))

    return render_template('register.html', form=form)


#User login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        #GEt user by Username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            #Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("You are now logged in as %s", username)
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid Login!"
                return render_template('login.html', error=error)
        else:
            error = "Username not found!"
            return render_template('login.html', error=error)

    return render_template('login.html')



#Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/jumbotron/')
def jumbotron():
    return render_template('jumbotron.html')
    
#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


#Class for Adding Menu
class MenuForm(Form):
    menu_type = SelectField('Menu Type', [validators.DataRequired()], choices=[('appetizers','Appetizer'),('main_dishes','Main Dish'),('desserts','Dessert'),('drinks','Drinks')], coerce=str)
    name = StringField('Name', [validators.Length(min=1, max=2000)])
    ingredients = TextAreaField('Ingredients', [validators.Length(min=10)])
    price = DecimalField('Price (Manat)', [validators.DataRequired()])


@app.route('/add_menu', methods=['GET','POST'])
@is_logged_in
def add_menu():
    form = MenuForm(request.form)
    if request.method == 'POST' and form.validate():

        #For uploading image
        target = os.path.join(APP_ROOT, 'static\img')
        print(target)

        #Checking if the directory exists
        if not os.path.isdir(target):
            os.mkdir(target)

        for file in request.files.getlist("file"):
            print(file)
            filename = file.filename
            destination = "\\".join([target, filename])
            print(destination)
            file.save(destination)

        #End of Uploading image

        menu_type = form.menu_type.data
        name = form.name.data
        ingredients = form.ingredients.data
        price = form.price.data
        image = filename

        #Create cursor
        cur = mysql.connection.cursor()

        #execute
        query = "INSERT INTO {}(name,ingredients,price,image) VALUES(%s, %s, %s, %s)".format(menu_type)
        cur.execute(query, (name,ingredients,price,image))

        #Commit to DB
        mysql.connection.commit()

        #CLose connection
        cur.close()

        flash(name+' is Added', 'success')

        return redirect(url_for(menu_type))


    return render_template('add_menu.html', form=form)

#Class for Editing Menu
class MenuEditForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=2000)])
    ingredients = TextAreaField('Ingredients', [validators.Length(min=10)])
    price = DecimalField('Price (Manat)', [validators.DataRequired()])
    image = FileField(u'Image File', [validators.DataRequired()])

#Editing the Appetizer
@app.route('/edit_app/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_app(id):

    #Create Cursor
    cur = mysql.connection.cursor()

    #Get appetizer by id
    result = cur.execute("SELECT * FROM appetizers WHERE id = %s", [id])

    appetizer = cur.fetchone()

    #Get Form
    form = MenuEditForm(request.form)

    #Populate appetizer form Fields
    form.name.data = appetizer['name']
    form.ingredients.data = appetizer['ingredients']
    form.price.data = appetizer['price']
    form.file.data = appetizer['image']


    if request.method == 'POST' and form.validate():

        #For uploading image
        target = os.path.join(APP_ROOT, 'static\img')
        print(target)

        #Checking if the directory exists
        if not os.path.isdir(target):
            os.mkdir(target)

        for file in request.files.getlist("file"):
            print(file)
            filename = file.filename
            destination = "\\".join([target, filename])
            print(destination)
            file.save(destination)
        #End of Uploading image

        name = request.form['name']
        ingredients = request.form['ingredients']
        price = request.form['price']
        image = request.form['image']

        #Create cursor
        cur = mysql.connection.cursor()

        #execute
        cur.execute("UPDATE appetizers SET name = %s, ingredients = %s, price = %s, image = %s WHERE id = %s", (name, ingredients, price, image, id))

        #Commit to DB
        mysql.connection.commit()

        #CLose connection
        cur.close()

        flash(name+' is Updated', 'success')

        return redirect(url_for('appetizers'))

    return render_template('edit_app.html', form=form)

#Deleting the Appetizer
@app.route('/delete_app/<string:id>', methods=['POST'])
@is_logged_in
def delete_app(id):
    #Creating a cursor
    cur = mysql.connection.cursor()

    #Execute
    cur.execute("DELETE FROM appetizers WHERE id = %s", [id])

    #Commit to DB
    mysql.connection.commit()

    #CLose connection
    cur.close()

    flash('Appetizer Deleted!', 'success')

    return redirect(url_for('appetizers'))

#Editing the Main Dish
@app.route('/edit_main/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_main(id):
    #Create Cursor
    cur = mysql.connection.cursor()

    #Get appetizer by id
    result = cur.execute("SELECT * FROM main_dishes WHERE id = %s", [id])

    main_dish = cur.fetchone()

    #Get Form
    form = MenuEditForm(request.form)

    #Populate main dish form Fields
    form.name.data = main_dish['name']
    form.ingredients.data = main_dish['ingredients']
    form.price.data = main_dish['price']
    form.image.data = main_dish['image']

    if request.method == 'POST' and form.validate():

        #For uploading image
        target = os.path.join(APP_ROOT, 'static\img')
        #print(target)

        #Checking if the directory exists
        if not os.path.isdir(target):
            os.mkdir(target)

        for file in request.files.getlist("file"):
            #print(file)
            filename = file.filename
            destination = "\\".join([target, filename])
            #print(destination)
            file.save(destination)
        #End of Uploading image

        name = request.form['name']
        ingredients = request.form['ingredients']
        price = request.form['price']
        image = request.form['file']

        #Create cursor
        cur = mysql.connection.cursor()

        #execute
        cur.execute("UPDATE main_dishes SET name = %s, ingredients = %s, price = %s, image = %s WHERE id = %s", (name, ingredients, price, image, id))

        #Commit to DB
        mysql.connection.commit()

        #CLose connection
        cur.close()

        flash(name + ' is Updated', 'success')

        return redirect(url_for('main_dishes'))

    return render_template('edit_main.html', form=form)



if __name__ == '__main__':
    app.secret_key='Larso0123'
    app.run(debug=True)
