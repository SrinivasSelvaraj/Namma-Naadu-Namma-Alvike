from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "127.0.0.1")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "MyDataBase")
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")

mysql = MySQL(app)

class Registerform(FlaskForm):
    Name = StringField("Name", validators=[DataRequired()])
    Email = StringField("Email", validators=[DataRequired(), Email()])
    Password = StringField("Password", validators=[DataRequired()])
    ConfirmPassword = PasswordField("Retype Password", validators=[
        DataRequired(),
        EqualTo('Password', message='Passwords must match.')
     ])
    Submit = SubmitField("Register")

class LoginForm(FlaskForm):
    Email = StringField("Email", validators=[DataRequired(), Email()])
    Password = PasswordField("Password", validators=[DataRequired()])
    Submit = SubmitField("Login")


@app.route('/')
def index():
    return render_template("Index.html")

@app.route('/Register', methods=['GET', 'POST'])
def Register():
    form = Registerform()
    if form.validate_on_submit():
        name = form.Name.data
        email = form.Email.data
        password = form.Password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already Registered. Try logging in.", "error")
            return redirect(url_for('Register'))

        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cursor.close()

        flash("Successfully Registered!", "success")
        return redirect(url_for('Login'))
    return render_template("Register.html", form=form)

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.Email.data
        password = form.Password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['username'] = user[1]  # Save user's name from DB
            flash("Login successful!", "success")
            return redirect(url_for('Welcome'))
        else:
            flash("Invalid email or password", "error")

    return render_template("Login.html", form=form)

@app.route('/Welcome')
def Welcome():
    if 'username' in session:
        username = session['username']
        return render_template("Welcome.html", username=username)
    else:
        flash("Please login first.", "error")
        return redirect(url_for('Login'))

@app.route('/en')
def en():
    return render_template("en.html")

@app.route('/Donate')
def Donate():
    return render_template("Donate.html")

@app.route('/ContactUs', methods=['GET', 'POST'])
def ContactUs():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        message = request.form['message']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO grievances (name, email, phone_number, message) VALUES (%s, %s, %s, %s)",
                (name, email, phone_number, message)
            )
            mysql.connection.commit()
            cursor.close()
            flash("Your enquiry has been submitted successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('ContactUs'))

        return redirect(url_for('ContactUs'))

    return render_template("ContactUs.html")


if __name__ == '__main__':
    app.run(debug=True)
