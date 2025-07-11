from flask import Flask, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
import os
from flask_bootstrap import Bootstrap5
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import flask_migrate


class BookForm(FlaskForm):
    book_name = StringField('Book name', validators=[DataRequired()])
    book_author = StringField('Author', validators=[DataRequired()])
    rating = StringField('Rating (out of 10 eg: 9/10)',
                         validators=[DataRequired()])
    add_book = SubmitField('Add Book')


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


app = Flask(__name__)
SECRET_KEY: bytes = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books-collection.db'
db.init_app(app)
bootstrap: Bootstrap5 = Bootstrap5(app)
csrf: CSRFProtect = CSRFProtect(app)


book_items: list = []


class Library(db.Model):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True)
    author: Mapped[str] = mapped_column(String(250))
    rating: Mapped[float]


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    global book_items
    
    return render_template('index.html', book_items=book_items)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = BookForm()
    if form.validate_on_submit():
        book_items.append(
            (form.book_name.data, form.book_author.data, form.rating.data)
        )
        with app.app_context():
            new_book = Library(title=form.book_name.data,
                               author=form.book_author.data,
                               rating=form.rating.data)
            db.session.add(new_book)
            db.session.commit()
        return redirect(url_for('home'))

    return render_template('add.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
