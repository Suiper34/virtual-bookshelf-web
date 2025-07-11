from flask import Flask, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
import os
from flask_bootstrap import Bootstrap5
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import flask_migrate

class BookForm(FlaskForm):
    book_name = StringField('Book name', validators=[DataRequired()])
    book_author = StringField('Author', validators=[DataRequired()])
    rating = StringField('Rating (out of 10 eg: 9/10)',
                         validators=[DataRequired()])
    add_book = SubmitField('Add Book')


app = Flask(__name__)
SECRET_KEY: bytes = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
bootstrap: Bootstrap5 = Bootstrap5(app)
csrf: CSRFProtect = CSRFProtect(app)

book_items: list = []


@app.route('/')
def home():
    global book_items
    return render_template('index.html', book_items=book_items)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = BookForm()
    if form.validate_on_submit():
        book_items.append(
            (form.book_name.data, form.book_author.data, form.add_book.data)
        )
        return redirect(url_for('home'))

    return render_template('add.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
