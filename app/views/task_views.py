# -*- coding: utf-8 -*-
# @Author: zhanglei
# @Time: 2020/6/29 20:51
# @File: task_views.py


from flask import Blueprint, jsonify
from app.models.task import Task

task_bp = Blueprint('task_page', __name__)


@task_bp.route('/task/list', methods=['GET', 'POST'])
def tasks():
    user_list = [user.to_dict() for user in Task.query.all() if user]
    return jsonify(user_list)


@task_bp.route('/task/update/<string:name>/<string:accessId>/<string:accessKey>')
def update(name, accessId, accessKey):
    user = Task.query.filter(Task.nickName == name).first()
    if user is not None:
        user.accessId = accessId
        user.accessKey = accessKey
        user.update()


@task_bp.route('/task/delete/<long:id>')
def delete(id):
    task = Task.query.filter(Task.id == id).first()
    if task is not None:
        task.delete()
