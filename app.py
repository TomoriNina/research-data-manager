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
    # 从首页的新增课题表单中获取用户输入的内容
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
    # 从数据库中查询该课题的名称、实验批次信息和实验参数信息
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
    cur.execute(
        "SELECT * FROM experiment_params WHERE batch_id IN (" \
        "SELECT batch_id FROM experiment_batches WHERE project_id=%s)",
        (project_id,)
    )
    params = cur.fetchall()
    cur.close()
    # 利用课题 ID 、名称、实验批次信息和实验参数信息渲染实验批次页面
    return render_template(
        "batch.html",
        project_id=project_id,
        project_name=project_name[0],
        batches=batches,
        params=params
    )

# 新增实验批次功能
@app.route("/add_batch", methods=['POST'])
def add_batch():
    # 从实验批次页面的新增批次表单中获取用户输入的内容
    project_id = request.form['project_id']
    batch_name = request.form['batch_name']
    experiment_date = request.form['experiment_date']
    remark = request.form['remark']
    # 向数据库中添加新增的实验批次
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO experiment_batches (project_id, batch_name, experiment_date, remark) VALUES (%s, %s, %s, %s)",
        (project_id, batch_name, experiment_date, remark)
    )
    mysql.connection.commit()
    cur.close()
    # 跳回实验批次页面
    return redirect(f"/batch/{project_id}")

# 新增实验参数功能
@app.route("/add_param", methods=['POST'])
def add_param():
    # 从实验批次页面的新增参数表单中获取用户输入的内容
    batch_id = request.form['batch_id']
    param_name = request.form['param_name']
    param_value = request.form['param_value']
    # 向数据库中添加新增的实验参数
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO experiment_params (batch_id, param_name, param_value) VALUES (%s, %s, %s)",
        (batch_id, param_name, param_value)
    )
    mysql.connection.commit()
    cur.close()
    # 跳回实验批次页面
    return redirect(f"/batch/{request.form['project_id']}")

if __name__ == "__main__":
    app.run(debug=True)