## Flask标准目录结构

### 目录结构说明
```text
.
├── README.md                   # 项目说明文件
├── app                         # Flask程序包
│   ├── __init__.py
│   ├── main                    # 主程序包
│   │   ├── __init__.py
│   │   ├── forms               # 表单处理模块包
│   │   │   └── __init__.py
│   │   ├── models              # 数据库ORM模块包
│   │   │   └── __init__.py
│   │   └── views               # 视图层模块包
│   │       └── __init__.py
│   │   └── src                 # 后台模块包
│   ├── static                  # 静态文件夹 css|js|jpg...
│   └── templates               # html渲染文件夹
├── scripts                     # 与项目相关的本地脚本 
├── config.py                   # 存储配置文件，具体信息参考文件
├── manage.py                   # 程序程序以及其它程序任务
├── migrations                  # 数据库迁移脚本
│   └── __init__.py
├── requirements.txt            # 程序依赖包列表
├── tests                       # 单元测试
│   └── __init__.py
└── venv                        # python虚拟环境
    └── __init__.py
