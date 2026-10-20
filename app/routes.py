import os
from flask import session, redirect, json, flash, url_for, redirect, render_template, current_app, request
from werkzeug.security import generate_password_hash, check_password_hash

from click import pass_context
from app import app
from app import db
from app.forms import RegisterForm, LoginForm, TopicForm, GroupForm, ChangeMemberForm, VenueForm, BookingForm
from app.models import Student, Topic, Group, Member, Venue, Booking

from flask_login import current_user, login_user, login_required, logout_user
from urllib.parse import urlsplit

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

"""
This file is a study buddy system designed so students can create study buddy groups with similar students doing the same topics.
It should allow them to:

USER SYSTEM
- Register
    - User model
    - Registration form
    - User-loader
    - Route
    - HTML template
- Login
    - Login form
    - Set/check password methods
    - Route
    - HTML template
- Logout
    - allow logout link

- Add/Delete topics
    - Form
    - Template
    - Model (topic, linked to groups somehow? 1 topic can be shared by many groups?)
    - Adjust Topics route


GROUPS SYSTEM
- Add a new group
    - Model (groups - linked to topics and users - many users can be members of many groups (?) and many groups can share 1 topic(?))
    - HTML template -
    - Form
    - Route
- Change group name
    - form
    - route edits
    - Need new HTML page? or can I add it to the same page? -> see if this is practical

- add/delete students based on username -> email students this happens to
    - Email.py file
    - Edit relationship between students and group (make sure username is shown, not ID)
    - ?
- only able to view group if not part of it, can't make edits/etc
    - 'if username in group' or smth

- View all groups in a system
    - Query


VENUE BOOKING SYSTEM
- Book a venue
    - Venue model (linked to groups - many groups can have a booking linked to a venue)
    - Form
    - HTML page

ALSO TO DO:
- Base html file
- Index
    - Show links to login/logout/register based on logged in/not
    - Link to view groups
    - Link to add topic/etc

"""

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(Student).where(Student.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: #if already logged in, passed to index
        return redirect(url_for('index'))
    form = RegisterForm() #if not, made to register
    if form.validate_on_submit():
        user = Student(username=form.username.data, email=form.email.data, student_id=form.student_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/topic', methods=['GET', 'POST'])
@login_required
def topic():
    form=TopicForm()
    topics=Topic.query.order_by(Topic.name).all()
    if form.validate_on_submit():
        topic = Topic(name=form.name.data)
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for('topic'))
    return render_template('topic.html', topics=topics, form=form)

@app.route('/edit_topic/<int:topic_id>', methods=['GET', 'POST'])
@login_required
def edit_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    form = TopicForm(obj=topic)
    if form.validate_on_submit():
        topic.name=form.name.data
        db.session.commit()
        return redirect(url_for('topic'))
    return render_template('edit_topic.html', form=form)

@app.route('/delete_topic/<int:topic_id>')
@login_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    db.session.delete(topic)
    db.session.commit()
    return redirect(url_for('topic'))

@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    groups=Group.query.order_by(Group.name).all()
    return render_template('groups.html', groups=groups)

@app.route('/add_group', methods=['GET', 'POST'])
@login_required
def add_group():
    form = GroupForm()
    form.topic.choices = [
        (t.id, t.name) for t in
        Topic.query.order_by(Topic.name).all()
    ]
    if form.validate_on_submit():
        group = Group(name=form.name.data,
                      topic_id=form.topic.data,
                      leader=current_user,
                      )
        try:
            db.session.add(group)
            db.session.commit()
            flash(f'Group added!')
            return redirect(url_for('groups'))
        except IntegrityError:
            db.session.rollback()
            flash(f'There was an error. Please try again.')
    return render_template('add_group.html', form=form)

@app.route('/manage_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def manage_group(group_id):
    form = ChangeMemberForm()
    group = Group.query.filter(Group.id==group_id).first()
    students = (
        Student.query #query table Student
        .join(Member, Member.student_id == Student.id) #Combine Member and Student so we can access data from Members that is linked to each student
        .filter(Member.group_id == group_id) #only include data from members who are in this group
        .all()
    )
    #Students currently in group who you can choose from to remove:
    form.students.choices = [(s.id, s.username) for s in students] #students to choose from on form = those from query

    current_ids = [s.id for s in students]
    available_students = Student.query.filter(~Student.id.in_(current_ids)).all() #NOT students in current_IDs
    #Students who are NOT currently in a group ('available students') who you could add to your group:
    form.student.choices = [(s.id, s.username) for s in available_students]

    if form.validate_on_submit():
        if form.remove.data: #if you select 'remove' submit button
            selected_ids = form.students.data
            print(selected_ids)
            Member.query.filter(
                Member.group_id == group_id,
                Member.student_id.in_(selected_ids)
            ).delete(synchronize_session=False) #delete members from the group_id

            db.session.commit()

        elif form.add.data:
            student_id = form.student.data

            #create association row
            link = Member(group_id=group_id, student_id=student_id)
            db.session.add(link)
            db.session.commit()

        return redirect(url_for('manage_group', group_id=group_id))
    return render_template('manage_group.html', group=group, students=students, form=form, group_id=group_id)

@app.route('/venues', methods=['GET', 'POST'])
@login_required
def venues():
    form = VenueForm()
    venues = Venue.query.order_by(Venue.name).all()
    if form.validate_on_submit():
        venue = Venue(name=form.name.data)
        db.session.add(venue)
        db.session.commit()
        return redirect(url_for('venues'))
    return render_template('venues.html', venues=venues, form=form)

@app.route('/bookings', methods=['GET', 'POST'])
@login_required
def bookings():
    bookings = Booking.query.order_by(Booking.start_time).all()
    form = BookingForm()

    groups = Group.query.order_by(Group.name).all()
    form.group.choices = [(g.id, g.name) for g in groups]

    venues = Venue.query.order_by(Venue.name).all()
    form.venue.choices = [(v.id, v.name) for v in venues]

    if form.validate_on_submit():
        b = Booking(group_id=form.group.data, venue_id=form.venue.data, start_time=form.start_time.data, end_time=form.end_time.data)
        db.session.add(b)
        db.session.commit()
        flash(f'Booking made!')
        return redirect(url_for('bookings'))
    else:
        flash(f'Error. Form did not validate.')
    return render_template('bookings.html', form=form, bookings=bookings)

