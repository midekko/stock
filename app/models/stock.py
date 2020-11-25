# -*- coding: utf-8 -*-
# @Author: zhanglei
# @Time: 2020/6/29 20:04
# @File: task.py

from datetime import datetime

from app import db


class Stock(db.Model):
    __tablename__ = 'stock'

    case_name = db.Column(db.String(128), nullable=False, primary_key=True)
    user_name = db.Column(db.String(256), nullable=False, primary_key=True)
    thedate = db.Column(db.String(12), nullable=False, primary_key=True)
    cn_stock = db.Column(db.Float, default=0)
    hk_stock = db.Column(db.Float, default=0)
    us_stock = db.Column(db.Float, default=0)
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, case_name, user_name, thedate, cn_stock, hk_stock, us_stock):
        super().__init__()
        self.case_name = case_name
        self.user_name = user_name
        self.thedate = thedate
        self.cn_stock = cn_stock
        self.hk_stock = hk_stock
        self.us_stock = us_stock
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

