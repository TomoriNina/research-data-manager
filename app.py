from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

# 创建 Flask 应用
app = Flask(__name__)

# 配置 MySQL 数据库
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1919810'
app.config['MYSQL_DB'] = 'research_data'

# 创建数据库链接对象
mysql = MySQL(app)

# 首页功能：展示所有课题
@app.route("/")
def index():
    # 从数据库查询所有课题的信息
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall() # fetchall() 的返回值为二维元组
    cur.close()
    # 利用课题信息渲染首页
    return render_template("index.html", projects=projects)

# 新增课题功能
@app.route("/add_project", methods=['POST'])
def add_project():
    # 从网页的新增课题表单中获取用户输入的内容
    project_name = request.form['project_name']
    researcher = request.form['researcher']
    remark = request.form['remark']
    # 向数据库中添加新增的课题
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO projects (project_name, researcher, remark) VALUES(%s, %s, %s)",
        (project_name, researcher, remark)
    )
    mysql.connection.commit()
    cur.close()
    # 跳回首页
    return redirect("/")

# 实验批次页面：展示某个课题的实验批次
@app.route("/batch/<int:project_id>")
def batch(project_id):
    # 从数据库中查询该课题的名称和实验批次信息
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT project_name FROM projects WHERE project_id=%s",
        (project_id,)
    )
    project_name = cur.fetchone() # fetchall() 的返回值为一维元组
    cur.execute(
        "SELECT * FROM experiment_batches WHERE project_id=%s",
        (project_id,)
    )
    batches = cur.fetchall()
    cur.close()
    # 利用课题 ID 、名称和实验批次信息渲染实验批次页面
    return render_template(
        "batch.html",
        project_id=project_id,
        project_name=project_name[0],
        batches=batches
    )

if __name__ == "__main__":
    app.run(debug=True)