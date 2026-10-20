from app import db
from app.models import *

def setup():
    db.create_all()

    #required setup
    db.session.add_all([Topic(name="AIML"),
                        Topic(name="BUS"),
                        Topic(name="SW2"),
                        ])

    db.session.add_all([Venue(name="Murray Learning Centre"),
                        Venue(name="JG Smith"),
                        Venue(name="Avon Building"),
                        ])

    # test data
    u = Student(username="test", email="test@gmail.com", student_id="2596008")
    u.set_password("12345")

    v = Student(username="Kate", email="test2@gmail.com", student_id="89221778")
    v.set_password("44")

    y = Student(username="Emma", email="test3@gmail.com", student_id="45289723")
    y.set_password("33")

    z = Student(username="Macey", email="test4@gmail.com", student_id="4362426764")
    z.set_password("22")

    j = Student(username="James", email="test5@gmail.com", student_id="435987298")
    j.set_password("11")

    g = Group(name='test group',
              topic_id=1,
              leader_id=4,
              )

    f = Group(name='test group 2',
              topic_id=2,
              leader_id=2,
              )

    m = Member(group_id=1,
               student_id=1)



    db.session.add(u)
    db.session.add(v)
    db.session.add(y)
    db.session.add(z)
    db.session.add(j)
    db.session.add(g)
    db.session.add(f)
    db.session.add(m)
    db.session.commit()