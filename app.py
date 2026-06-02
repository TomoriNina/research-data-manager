from flask import Flask, render_template, request, redirect, send_file
from flask_mysqldb import MySQL
import os


app = Flask(__name__)

# MySQL 配置
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1919810'
app.config['MYSQL_DB'] = 'research_data'

# 文件上传配置
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mysql = MySQL(app)

# ==================== 课题管理 ====================
@app.route("/")
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.close()
    return render_template("index.html", projects=projects)

@app.route("/add_project", methods=['POST'])
def add_project():
    project_name = request.form['project_name']
    researcher = request.form['researcher']
    create_date = request.form['create_date']
    remark = request.form['remark']
    cur = mysql.connection.cursor()
    # 若用户填写了课题创建日期，则正常向数据库添加新增的课题
    if create_date:
        cur.execute(
            "INSERT INTO projects (project_name, researcher, create_date, remark) VALUES (%s, %s, %s, %s)",
            (project_name, researcher, create_date, remark)
        )
    # 若未填写日期，则不插入日期字段，使 MySQL 使用默认日期
    else:
        cur.execute(
            "INSERT INTO projects (project_name, researcher, remark) VALUES (%s, %s, %s)",
            (project_name, researcher, remark)
        )
    mysql.connection.commit()
    cur.close()
    return redirect("/")

@app.route("/edit_project/<int:project_id>")
def edit_project(project_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM projects WHERE project_id=%s",
        (project_id,)
    )
    project = cur.fetchone()
    cur.close()
    return render_template("edit_project.html", project=project)

@app.route("/update_project", methods=['POST'])
def update_project():
    project_id = request.form['project_id']
    project_name = request.form['project_name']
    researcher = request.form['researcher']
    create_date = request.form['create_date']
    remark = request.form['remark']
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE projects SET project_name=%s, researcher=%s, create_date=%s, remark=%s WHERE project_id=%s",
        (project_name, researcher, create_date, remark, project_id)
    )
    mysql.connection.commit()
    cur.close()
    return redirect("/")

@app.route("/delete_project/<int:project_id>")
def delete_project(project_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "DELETE FROM projects WHERE project_id=%s",
        (project_id,)
    )
    mysql.connection.commit()
    cur.close()
    return redirect("/")

# ==================== 实验批次管理 ====================
@app.route("/batch/<int:project_id>")
def batch(project_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT project_name FROM projects WHERE project_id=%s",
        (project_id,)
    )
    project_name = cur.fetchone()[0]
    cur.execute(
        "SELECT * FROM experiment_batches WHERE project_id=%s",
        (project_id,)
    )
    batches = cur.fetchall()
    cur.close()
    return render_template(
        "batch.html",
        project_id=project_id,
        project_name=project_name,
        batches=batches
    )

@app.route("/add_batch", methods=['POST'])
def add_batch():
    project_id = request.form['project_id']
    batch_name = request.form['batch_name']
    experiment_date = request.form['experiment_date']
    remark = request.form['remark']
    cur = mysql.connection.cursor()
    if experiment_date:
        cur.execute(
            "INSERT INTO experiment_batches (project_id, batch_name, experiment_date, remark) VALUES (%s, %s, %s, %s)",
            (project_id, batch_name, experiment_date, remark)
        )
    else:
        cur.execute(
            "INSERT INTO experiment_batches (project_id, batch_name, remark) VALUES (%s, %s, %s)",
            (project_id, batch_name, remark)
        )
    mysql.connection.commit()
    cur.close()
    return redirect(f"/batch/{project_id}")

@app.route("/edit_batch/<int:batch_id>")
def edit_batch(batch_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM experiment_batches WHERE batch_id=%s",
        (batch_id,)
    )
    batch = cur.fetchone()
    cur.close()
    return render_template("edit_batch.html", batch=batch)

@app.route("/update_batch", methods=['POST'])
def update_batch():
    project_id = request.form['project_id']
    batch_id = request.form['batch_id']
    batch_name = request.form['batch_name']
    experiment_date = request.form['experiment_date']
    remark = request.form['remark']
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE experiment_batches SET batch_name=%s, experiment_date=%s, remark=%s WHERE batch_id=%s",
        (batch_name, experiment_date, remark, batch_id)
    )
    mysql.connection.commit()
    cur.close()
    return redirect(f"/batch/{project_id}")

@app.route("/delete_batch/<int:batch_id>/<int:project_id>")
def delete_batch(batch_id, project_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "DELETE FROM experiment_batches WHERE batch_id=%s",
        (batch_id,)
    )
    mysql.connection.commit()
    cur.close()
    return redirect(f"/batch/{project_id}")

# ==================== 实验参数管理 ====================
@app.route("/param/<int:batch_id>")
def param(batch_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT batch_name, project_id FROM experiment_batches WHERE batch_id=%s",
        (batch_id,)
    )
    batch_name, project_id = cur.fetchone()
    cur.execute(
        "SELECT * FROM experiment_params WHERE batch_id=%s",
        (batch_id,)
    )
    params = cur.fetchall()
    cur.close()
    return render_template(
        "param.html",
        batch_id=batch_id,
        batch_name=batch_name,
        project_id=project_id,
        params=params
    )

@app.route("/add_param", methods=['POST'])
def add_param():
    batch_id = request.form['batch_id']
    param_name = request.form['param_name']
    param_value = request.form['param_value']
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO experiment_params (batch_id, param_name, param_value) VALUES (%s, %s, %s)",
        (batch_id, param_name, param_value)
    )
    mysql.connection.commit()
    cur.close()
    return redirect(f"/param/{batch_id}")

@app.route("/edit_param/<int:param_id>")
def edit_param(param_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM experiment_params WHERE param_id=%s",
        (param_id,)
    )
    param = cur.fetchone()
    cur.close()
    return render_template("edit_param.html", param=param)

@app.route("/update_param", methods=['POST'])
def update_param():
    batch_id = request.form['batch_id']
    param_id = request.form['param_id']
    param_name = request.form['param_name']
    param_value = request.form['param_value']
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE experiment_params SET param_name=%s, param_value=%s WHERE param_id=%s",
        (param_name, param_value, param_id)
    )
    mysql.connection.commit()
    cur.close()
    return redirect(f"/param/{batch_id}")

@app.route("/delete_param/<int:param_id>/<int:batch_id>")
def delete_param(param_id, batch_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "DELETE FROM experiment_params WHERE param_id=%s",
        (param_id,)
    )
    mysql.connection.commit()
    cur.close()
    return redirect(f"/param/{batch_id}")

# ==================== 数据文件管理 ====================件
@app.route("/file/<int:batch_id>")
def file(batch_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT batch_name FROM experiment_batches WHERE batch_id=%s",
        (batch_id,)
    )
    batch_name = cur.fetchone()[0]
    cur.execute(
        "SELECT * FROM data_files WHERE batch_id=%s",
        (batch_id,)
    )
    files = cur.fetchall()
    cur.close()
    return render_template(
        "file.html",
        batch_id=batch_id,
        batch_name=batch_name,
        files=files
    )

@app.route("/upload_file", methods=['POST'])
def upload_file():
    batch_id = request.form['batch_id']
    file = request.files['file']
    if file:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT MAX(version) FROM data_files WHERE batch_id=%s",
            (batch_id,)
        )
        max_version = cur.fetchone()[0]
        new_version = max_version + 1 if max_version else 1 # 新版本号为当前最大版本号加 1
        # 根据批次 ID 和版本号重命名文件并存储
        raw_name, ext = os.path.splitext(file.filename)
        file_name = f"{raw_name}_{batch_id}_{new_version}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)
        cur.execute(
            "INSERT INTO data_files (batch_id, file_name, file_path, version) VALUES (%s, %s, %s, %s)",
            (batch_id, file_name, file_path, new_version)
        )
        mysql.connection.commit()
        cur.close()
    return redirect(f"/file/{batch_id}")

@app.route("/delete_file/<int:file_id>/<int:batch_id>")
def delete_file(file_id, batch_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT file_path FROM data_files WHERE file_id=%s",
        (file_id,)
    )
    file_path = cur.fetchone()[0]
    if os.path.isfile(file_path):
        os.remove(file_path)
    cur.execute(
        "DELETE FROM data_files WHERE file_id=%s",
        (file_id,)
    )
    mysql.connection.commit()
    cur.close()
    return redirect(f"/file/{batch_id}")

@app.route("/download_file/<int:file_id>")
def download_file(file_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT file_name, file_path FROM data_files WHERE file_id=%s",
        (file_id,)
    )
    file_name, file_path = cur.fetchone()
    cur.close()
    return send_file(file_path, as_attachment=True, download_name=file_name)


if __name__ == "__main__":
    app.run(debug=True)