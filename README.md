# 科研数据管理系统
这是一个用于个人练习的项目

## 项目依赖
    MySQL 9.7.0
    python 3.12.13
    flask 3.1.3
    flask-mysqldb 2.0.0

## 数据库搭建步骤
1. 打开 MySQL 管理工具（Navicat/DBeaver 等）
2. 执行 `create_database.sql` 脚本以创建科研数据库
3. 修改 `app.py` 脚本的第 11 行 `app.config['MYSQL_PASSWORD']` 的值为你的 MySQL 本地密码

## 运行项目
1. 安装所需依赖
2. 运行 `app.py` 脚本
3. 访问 http://127.0.0.1:5000

## 发行版本
改用 SQLite 作为数据库系统，并将项目打包为可执行文件