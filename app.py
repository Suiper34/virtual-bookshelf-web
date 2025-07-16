import os

from flask import Flask, flash, redirect, render_template, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import String, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class BookForm(FlaskForm):
    book_name = StringField('Book name', validators=[
                            DataRequired(), Length(max=250)])
    book_author = StringField('Author', validators=[
                              DataRequired(), Length(max=250)])
    rating = FloatField('Rating (out of 10 eg: 9.5/10)',
                        validators=[DataRequired(), NumberRange(min=0, max=10)])
    add_book = SubmitField('Add Book')


class EditRating(FlaskForm):
    rating = FloatField(
        'Edit Rating (out of 10 eg: 9.5/10)',
        validators=[DataRequired(), NumberRange(min=0, max=10)]
    )
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
    __tablename__: str = 'bookshelf'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True)
    author: Mapped[str] = mapped_column(String(250))
    rating: Mapped[float]


# with app.app_context():
#     # db.create_all()

@app.route('/')
def home():
    """
    Executes a SELECT query for all books ordered by title
    passes the book list to index.html template
    shows empty library message if no books exist

    Returns:
        rendered HTML template showing all books
    """
    result = db.session.execute(select(Library).order_by(Library.title))
    all_books = result.scalars().all()

    return render_template('index.html', book_items=all_books)


@app.route('/add', methods=['POST', 'GET'])
def add():
    """
    GET:
        Displays empty book addition form
    Returns:
        rendered add.html template

    POST:
        validates form data and commits new book to database
    Returns:
        redirect to home page after successful submission
    """

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
    """
    Args:
        book_id (int): primary key of book to edit

    GET:
        fetches book by ID, pre-populates form with current rating \
        and renders edit form
    Returns:
        rendered edit-rating.html template

    POST:
        validates new rating and executes UPDATE query
    Returns:
        redirect to home page after save
    """
    result = db.session.execute(
        select(Library).where(Library.id == book_id))
    book_to_update = result.scalar_one_or_none()

    if book_to_update is None:
        flash('Book not found!', category='danger')
        return redirect(url_for('home'))

    form = EditRating()

    if form.validate_on_submit():
        # update rating
        db.session.execute(
            update(Library).where(Library.id == book_id).values(
                rating=form.rating.data)
        )
        db.session.commit()
        flash('Book rating updated successfully!', category='success')
        return redirect(url_for('home'))

    return render_template('edit-rating.html', form=form, book=book_to_update)


@app.route('/delete/<int:book_id>')
def delete_book(book_id: int):
    """
    Args:
        book_id (int): primary key of book to delete

    executes DELETE query and shows appropriate flash message

    Returns:
        redirect to home page
    """

    book_to_delete = db.session.get(Library, book_id)

    if book_to_delete:
        db.session.delete(book_to_delete)
        db.session.commit()
        flash('Book has been deleted!', category='success')

    else:
        flash('Book does not exist in the bookshelf!', category='error')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
