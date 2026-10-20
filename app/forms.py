from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectMultipleField, SelectField, IntegerField, TextAreaField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, NumberRange, Length, EqualTo, ValidationError
from wtforms.fields.datetime import DateField, DateTimeLocalField
from datetime import date

from app.models import Student
from app import db, login
import sqlalchemy as sa


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    student_id = StringField("Student ID", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign In")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(Student).where(Student.username == username.data))
        if user is not None:
            raise ValidationError('Username already in use.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(Student).where(Student.email == email.data))
        if user is not None:
            raise ValidationError('Email already in use.')

    def validate_student_id(self, student_id):
        user = db.session.scalar(sa.select(Student).where(Student.student_id == student_id.data))
        if user is not None:
            raise ValidationError('Student ID already in use.')


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class TopicForm(FlaskForm):
    name = StringField("Topic", validators=[DataRequired()])
    submit = SubmitField("Update Topics")

class GroupForm(FlaskForm):
    name = StringField("Group Name", validators=[DataRequired()])
    topic = SelectField("Topic", coerce=int)
    submit = SubmitField("Create Group")

class ChangeMemberForm(FlaskForm):
    students = SelectMultipleField("Students in this group", coerce=int)
    remove = SubmitField('Remove Student(s)')
    student = SelectField("Add Student", coerce=int)
    add = SubmitField('Add Student')

class BookingForm(FlaskForm):
    group = SelectField("Select Group", coerce=int)
    venue = SelectField("Select Venue", coerce=int)
    start_time = DateTimeLocalField(
        "Start Time",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )

    end_time = DateTimeLocalField(
        "End Time",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )

    submit = SubmitField('Make Booking')

class VenueForm(FlaskForm):
    name = StringField("Venue Name", validators=[DataRequired()])
    submit = SubmitField('Add Venue')