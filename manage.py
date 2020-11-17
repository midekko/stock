# -*- encoding: utf-8 -*-
"""
    package.module
    ~~~~~~~~~~~~~~

    project startup script

    # 1. python manage.py db init # 第一次初始化
    # 2. python manage.py db upgrade # 更新数据库
    # 3. python manage.py runserver # 运行服务
    # 4. python manage.py shell # 运行交互shell
    # 5. python manage.py db migrate -m "initial migration" # 检查表与字段

    :copyright: (c)  2018/5/22 by zwhset.
    :license: OPS, see LICENSE_FILE for more details.
"""

import os
from app import create_app, db
from app.models.user import User  # 引入models
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, user=User)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
