from flask import Flask, render_template, url_for, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.csrf import CSRFProtect
import os
from flask_bootstrap import Bootstrap5
from sqlalchemy import String, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy


class BookForm(FlaskForm):
    book_name = StringField('Book name', validators=[DataRequired()])
    book_author = StringField('Author', validators=[
                              DataRequired(), NumberRange(min=0, max=10)])
    rating = FloatField('Rating (out of 10 eg: 9.5/10)',
                        validators=[DataRequired()])
    add_book = SubmitField('Add Book')


class EditRating(FlaskForm):
    rating = FloatField('Edit Rating (out of 10 eg: 9.5/10)',
                        validators=[DataRequired(), NumberRange(min=0, max=10)])
    edit_save = SubmitField('Save Edit')


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


app = Flask(__name__)
SECRET_KEY: bytes = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books-collection.db'
app.config['SQLALCHEMY_ECHO'] = True  # for debugging SQL queries
db.init_app(app)
bootstrap: Bootstrap5 = Bootstrap5(app)
csrf: CSRFProtect = CSRFProtect(app)


book_items: list = []


class Library(db.Model):
    __tablename__: str = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True)
    author: Mapped[str] = mapped_column(String(250))
    rating: Mapped[float]


# with app.app_context():
#     # db.create_all()

@app.route('/')
def home():

    result = db.session.execute(db.select(Library).order_by(Library.title))
    all_books = result.scalars().all

    return render_template('index.html', book_items=all_books)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = BookForm()

    if form.validate_on_submit():

        new_book = Library(title=form.book_name.data,
                           author=form.book_author.data,
                           rating=form.rating.data)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add.html', form=form)


@app.route('/edit-rating/<int:book_id>', methods=['POST', 'GET'])
def edit_rating(book_id: int):
    result = db.session.execute(
        db.select(Library).where(Library.id == book_id))
    book_to_update = result.scalar_one_or_none()

    if book_to_update is None:
        flash('Book not found!', 'danger')
        return redirect(url_for('home'))

    form = EditRating()

    if form.validate_on_submit():
        # update rating
        db.session.execute(
            update(Library).where(Library.id == book_id)
        ).values(rating=form.rating.data)
        db.session.commit()
        flash('Book rating updated successfully!', 'success')
        return redirect(url_for('home'))

    form.rating.data = book_to_update.rating
    return render_template('edit-rating.html', form=form, book=book_to_update)


if __name__ == '__main__':
    app.run(debug=True)
