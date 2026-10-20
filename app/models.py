from tokenize import group

from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy.orm as so
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from flask_login import UserMixin
from app import db, login

# ADD ALL REQUIRED RELATIONSHIPS
# YOU MAY ADD ANY FIELDS YOU NEED
# YOU MAY ADD ANY TABLES YOU NEED


class Student(db.Model, UserMixin):
    __tablename__ = 'student'
    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    username: so.Mapped[str] = so.mapped_column(db.String, index= True, unique=True)
    email: so.Mapped[str] = so.mapped_column(db.String, index=True, unique=True)
    student_id: so.Mapped[str] = so.mapped_column(db.String, index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(db.String, unique=True)

    #In m:n relationship with groups - broken up by associative table 'member'.
    #In 1:m relationship with Member.
    members: Mapped[list['Member']] = relationship("Member", back_populates="student")

    #in 1:m relationship with Group (1 leader can manage many groups??)


    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


class Topic(db.Model):
    __tablename__ = 'topic'
    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(db.String, unique=True)

    #in 1:m relationship with groups
    groups: Mapped[list['Group']] = relationship("Group", back_populates="topic") #'one' side
        #there will be a list of groups sharing a topic. 'Group' in single quotes as not created yet.
        #in 1:m relationships with Group ('1' side - many groups can share 1 topic).

class Group(db.Model):
    __tablename__ = 'group'
    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(db.String, unique=True)

    # in m:1 relationship with topic - many groups can share a topic.
    topic_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("topic.id")) #'many' side (has PK of 'one' side as FK) -- References values from id column in topic table
    topic = so.relationship("Topic", back_populates="groups") #back_populates links it back to topics - this is the many side so groups is plural.

    #in m:1 relationship with User - this is why it has FK this side. Needed to look at ans for this one, it was a bit weird.
    leader_id: so.Mapped[str] = so.mapped_column(sa.ForeignKey("student.id")) #Many groups can share a leader - FK on this side.
    leader = so.relationship("Student", foreign_keys=[leader_id]) #Doesn't seem to be linking side? Why no back_populates??

    #In m:n relationship with Venue so...
    #in 1:m relationship with bookings
    bookings: Mapped[list['Booking']] = relationship("Booking", back_populates="group") #1 side

    #in 1:m relationship with student_groups (renamed to member so I don't go insane)
    members: Mapped[list['Member']] = relationship("Member", back_populates="group") #'one' side
        #There will be a list of members sharing a group.


class Member(db.Model):
    __tablename__ = 'member'
    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    #in m:1 relationship with Group and Student. Is the Associative table.
    group_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("group.id")) #'Many' side (has PK of 1 side as FK)
    group = so.relationship("Group", back_populates="members") #Links back to group. Many side - members is plural.

    student_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("student.id")) #Many side
    student = so.relationship("Student", back_populates="members") #Links back to Student. Many side - members is plural.


class Venue(db.Model):
    __tablename__ = 'venue'
    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(db.String, unique=True)

    #In m:n relationship with group so...
    #in 1:m relationship with booking
    bookings: Mapped[list['Booking']] = relationship("Booking", back_populates="venue") #1 side

class Booking(db.Model):
    __tablename__ = 'booking'
    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)

    #Associative table linking group and venue
    #In m:1 relationship with Group and Venue
    group_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("group.id")) #many side
    group = so.relationship("Group", back_populates="bookings")  # Links back to group. Many side - bookings is plural.

    venue_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("venue.id"))  # many side
    venue = so.relationship("Venue", back_populates="bookings")  # Links back to venue. Many side - bookings is plural.

    start_time = so.mapped_column(db.DateTime, nullable=False)
    end_time = so.mapped_column(db.DateTime, nullable=False)


@login.user_loader
def load_user(student_id: int):
    return db.session.get(Student, student_id)
