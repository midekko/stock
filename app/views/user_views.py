# -*- encoding: utf-8 -*-
"""
    package.module
    ~~~~~~~~~~~~~~

    Example index page.

    :copyright: (c)  2018/5/22 by zwhset.
    :license: OPS, see LICENSE_FILE for more details.
"""

from flask import Blueprint, jsonify
from app.models.user import User

user_bp = Blueprint('user_page', __name__)


@user_bp.route('/user/list', methods=['GET', 'POST'])
def users():
    user_list = [user.to_dict() for user in User.query.all() if user]
    return jsonify(user_list)


@user_bp.route('/user/update/<string:name>/<string:accessId>/<string:accessKey>')
def update(name, accessId, accessKey):
    user = User.query.filter(User.nickName == name).first()
    if user is not None:
        user.accessId = accessId
        user.accessKey = accessKey
        user.update()


@user_bp.route('/user/delete/<string:name>')
def delete(name):
    user = User.query.filter(User.nickName == name).first()
    if user is not None:
        user.delete()
        return 'success'
