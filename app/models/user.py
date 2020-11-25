# -*- encoding: utf-8 -*-
"""
    package.module
    ~~~~~~~~~~~~~~
"""

from datetime import datetime
from app import db


class User(Model):
    __tablename__ = 'user'  # 表名

    __table_args__ = {  # 表参数
        # 'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickName = db.Column(db.VARCHAR(55), unique=True, nullable=False)
    realName = db.Column(db.VARCHAR(55), unique=True)
    accessId = db.Column(db.String(256), default='')
    accessKey = db.Column(db.String(256), default='')
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, nickName, realName, accessId, accessKey, created, updated):
        super().__init__()
        self.nickName = nickName
        self.realName = realName
        self.accessId = accessId
        self.accessKey = accessKey
        self.created = created
        if not updated:
            self.updated = datetime.now()
        else:
            self.updated = updated

    def __repr__(self):
        return '<User %r>' % self.nickName

    def to_dict(self):
        data = dict(id=self.id,
                    nickName=self.nickName,
                    realName=self.realName,
                    accessId=self.accessId,
                    accessKey=self.accessKey,
                    created=self.created,
                    updated=self.updated)
        return data
