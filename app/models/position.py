# -*- coding: utf-8 -*-
# @Author: zhanglei
# @Time: 2020/6/29 20:04
# @File: position.py

from datetime import datetime

from app import db


class Position(db.Model):
    __tablename__ = 'position'

    case_name = db.Column(db.String(128), nullable=False, primary_key=True)
    user_name = db.Column(db.String(256), nullable=False, primary_key=True)
    hold_code = db.Column(db.String(30), nullable=False, primary_key=True)
    hold_category = db.Column(db.String(20), nullable=False)
    hold_num = db.Column(db.Float, default=0)
    hold_price = db.Column(db.Float, default=0)
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, case_name, user_name, hold_category, hold_code, hold_num, hold_price):
        super().__init__()
        self.case_name = case_name
        self.user_name = user_name
        self.hold_category = hold_category
        self.hold_code = hold_code
        self.hold_num = hold_num
        self.hold_price = hold_price
        self.created = datetime.now()
        self.updated = datetime.now()

    # def __repr__(self):
    #     return '<Stock %r>' % self.caseName

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        db.session.merge(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
