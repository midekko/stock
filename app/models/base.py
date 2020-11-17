# # -*- coding: utf-8 -*-
# # @Author: zhanglei
# # @Time: 2020/6/29 20:20
# # @File: base.py
#
# from app import db
#
#
# class Model(db.Model):
#     def __init__(self):
#         super().__init__()
#
#     def save(self):
#         db.session.add(self)
#         db.session.commit()
#         return self
#
#     def update(self):
#         db.session.commit()
#         return self
#
#     def delete(self):
#         db.session.delete(self)
#         db.session.commit()
