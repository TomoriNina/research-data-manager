from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os
import sys


app = Flask(__name__)

# ==================== SQLite 配置 ====================
def get_db_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(".")
    return os.path.join(base_dir, "research_data.db")

def init_database():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.execute('''CREATE TABLE IF NOT EXISTS `projects` (
        `project_id` integer PRIMARY KEY AUTOINCREMENT,
        `project_name` text NOT NULL,
        `researcher` text NOT NULL,
        `create_date` date DEFAULT (DATE('now')),
        `remark` text
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS `experiment_batches` (
        `batch_id` integer PRIMARY KEY AUTOINCREMENT,
        `batch_name` text NOT NULL,
        `project_id` integer NOT NULL,
        `experiment_date` date DEFAULT (DATE('now')),
        `remark` text,
        FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`) ON DELETE CASCADE
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS `experiment_params` (
        `param_id` integer PRIMARY KEY AUTOINCREMENT,
        `param_name` text NOT NULL,
        `param_value` text NOT NULL,
        `batch_id` integer NOT NULL,
        FOREIGN KEY (`batch_id`) REFERENCES `experiment_batches` (`batch_id`) ON DELETE CASCADE
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS `data_files` (
        `file_id` integer PRIMARY KEY AUTOINCREMENT,
        `file_name` text NOT NULL,
        `file_path` text NOT NULL,
        `version` integer DEFAULT NULL,
        `batch_id` integer NOT NULL,
        FOREIGN KEY (`batch_id`) REFERENCES `experiment_batches` (`batch_id`) ON DELETE CASCADE
    )''')
    conn.commit()
    conn.close()

init_database()

def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = None # 设置查询结果为元组形式
    return conn

# ==================== 课题管理 ====================
@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    conn.close()
    return render_template("index.html", projects=projects)

@app.route("/add_project", methods=['POST'])
def add_project():
    project_name = request.form['project_name']
    researcher = request.form['researcher']
    create_date = request.form['create_date']
    remark = request.form['remark']
    conn = get_db()
    cur = conn.cursor()
    # 若用户填写了课题创建日期，则正常向数据库添加新增的课题
    if create_date:
        cur.execute(
            "INSERT INTO projects (project_name, researcher, create_date, remark) VALUES (?, ?, ?, ?)",
            (project_name, researcher, create_date, remark)
        )
    # 若未填写日期，则不插入日期字段，使 SQLite 使用默认日期
    else:
        cur.execute(
            "INSERT INTO projects (project_name, researcher, remark) VALUES (?, ?, ?)",
            (project_name, researcher, remark)
        )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/edit_project/<int:project_id>")
def edit_project(project_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM projects WHERE project_id=?",
        (project_id,)
    )
    project = cur.fetchone()
    conn.close()
    return render_template("edit_project.html", project=project)

@app.route("/update_project", methods=['POST'])
def update_project():
    project_id = request.form['project_id']
    project_name = request.form['project_name']
    researcher = request.form['researcher']
    create_date = request.form['create_date']
    remark = request.form['remark']
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE projects SET project_name=?, researcher=?, create_date=?, remark=? WHERE project_id=?",
        (project_name, researcher, create_date, remark, project_id)
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_project/<int:project_id>")
def delete_project(project_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM projects WHERE project_id=?",
        (project_id,)
    )
    conn.commit()
    conn.close()
    return redirect("/")

# ==================== 实验批次管理 ====================
@app.route("/batch/<int:project_id>")
def batch(project_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT project_name FROM projects WHERE project_id=?",
        (project_id,)
    )
    project_name = cur.fetchone()[0]
    cur.execute(
        "SELECT * FROM experiment_batches WHERE project_id=?",
        (project_id,)
    )
    batches = cur.fetchall()
    conn.close()
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
    conn = get_db()
    cur = conn.cursor()
    if experiment_date:
        cur.execute(
            "INSERT INTO experiment_batches (project_id, batch_name, experiment_date, remark) VALUES (?, ?, ?, ?)",
            (project_id, batch_name, experiment_date, remark)
        )
    else:
        cur.execute(
            "INSERT INTO experiment_batches (project_id, batch_name, remark) VALUES (?, ?, ?)",
            (project_id, batch_name, remark)
        )
    conn.commit()
    conn.close()
    return redirect(f"/batch/{project_id}")

@app.route("/edit_batch/<int:batch_id>")
def edit_batch(batch_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM experiment_batches WHERE batch_id=?",
        (batch_id,)
    )
    batch = cur.fetchone()
    conn.close()
    return render_template("edit_batch.html", batch=batch)

@app.route("/update_batch", methods=['POST'])
def update_batch():
    project_id = request.form['project_id']
    batch_id = request.form['batch_id']
    batch_name = request.form['batch_name']
    experiment_date = request.form['experiment_date']
    remark = request.form['remark']
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE experiment_batches SET batch_name=?, experiment_date=?, remark=? WHERE batch_id=?",
        (batch_name, experiment_date, remark, batch_id)
    )
    conn.commit()
    conn.close()
    return redirect(f"/batch/{project_id}")

@app.route("/delete_batch/<int:batch_id>/<int:project_id>")
def delete_batch(batch_id, project_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM experiment_batches WHERE batch_id=?",
        (batch_id,)
    )
    conn.commit()
    conn.close()
    return redirect(f"/batch/{project_id}")

# ==================== 实验参数管理 ====================
@app.route("/param/<int:batch_id>")
def param(batch_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT batch_name, project_id FROM experiment_batches WHERE batch_id=?",
        (batch_id,)
    )
    batch_name, project_id = cur.fetchone()
    cur.execute(
        "SELECT * FROM experiment_params WHERE batch_id=?",
        (batch_id,)
    )
    params = cur.fetchall()
    conn.close()
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
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO experiment_params (batch_id, param_name, param_value) VALUES (?, ?, ?)",
        (batch_id, param_name, param_value)
    )
    conn.commit()
    conn.close()
    return redirect(f"/param/{batch_id}")

@app.route("/edit_param/<int:param_id>")
def edit_param(param_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM experiment_params WHERE param_id=?",
        (param_id,)
    )
    param = cur.fetchone()
    conn.close()
    return render_template("edit_param.html", param=param)

@app.route("/update_param", methods=['POST'])
def update_param():
    batch_id = request.form['batch_id']
    param_id = request.form['param_id']
    param_name = request.form['param_name']
    param_value = request.form['param_value']
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE experiment_params SET param_name=?, param_value=? WHERE param_id=?",
        (param_name, param_value, param_id)
    )
    conn.commit()
    conn.close()
    return redirect(f"/param/{batch_id}")

@app.route("/delete_param/<int:param_id>/<int:batch_id>")
def delete_param(param_id, batch_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM experiment_params WHERE param_id=?",
        (param_id,)
    )
    conn.commit()
    conn.close()
    return redirect(f"/param/{batch_id}")

# ==================== 数据文件管理 ====================
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) 

@app.route("/file/<int:batch_id>")
def file(batch_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT batch_name FROM experiment_batches WHERE batch_id=?",
        (batch_id,)
    )
    batch_name = cur.fetchone()[0]
    cur.execute(
        "SELECT * FROM data_files WHERE batch_id=?",
        (batch_id,)
    )
    files = cur.fetchall()
    conn.close()
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
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT MAX(version) FROM data_files WHERE batch_id=?",
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
            "INSERT INTO data_files (batch_id, file_name, file_path, version) VALUES (?, ?, ?, ?)",
            (batch_id, file_name, file_path, new_version)
        )
        conn.commit()
        conn.close()
    return redirect(f"/file/{batch_id}")

@app.route("/delete_file/<int:file_id>/<int:batch_id>")
def delete_file(file_id, batch_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT file_path FROM data_files WHERE file_id=?",
        (file_id,)
    )
    file_path = cur.fetchone()[0]
    if os.path.isfile(file_path):
        os.remove(file_path)
    cur.execute(
        "DELETE FROM data_files WHERE file_id=?",
        (file_id,)
    )
    conn.commit()
    conn.close()
    return redirect(f"/file/{batch_id}")

@app.route("/download_file/<int:file_id>")
def download_file(file_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT file_name, file_path FROM data_files WHERE file_id=?",
        (file_id,)
    )
    file_name, file_path = cur.fetchone()
    conn.close()
    return send_file(file_path, as_attachment=True, download_name=file_name)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)