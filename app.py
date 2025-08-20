from flask import Flask, request, redirect, render_template, url_for, send_from_directory
import sqlite3, os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db()
    if request.method == 'POST':
        job_name = request.form['job_name']
        notes = request.form['notes']
        approved = 1 if request.form.get('approved') == 'on' else 0
        conn.execute("INSERT INTO jobs (job_name, notes, approved) VALUES (?, ?, ?)", (job_name, notes, approved))
        conn.commit()
        job_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Handle video uploads
        for file in request.files.getlist('videos'):
            if file.filename:
                filename = f"{job_id}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conn.execute("INSERT INTO videos (job_id, filename) VALUES (?, ?)", (job_id, filename))
                conn.commit()
        return redirect('/')
    jobs = conn.execute("SELECT * FROM jobs").fetchall()
    return render_template('index.html', jobs=jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    conn = get_db()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    videos = conn.execute("SELECT * FROM videos WHERE job_id = ?", (job_id,)).fetchall()
    return render_template('job_detail.html', job=job, videos=videos)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    conn = get_db()
    if request.method == 'POST':
        job_name = request.form['job_name']
        notes = request.form['notes']
        approved = 1 if request.form.get('approved') == 'on' else 0
        conn.execute("INSERT INTO jobs (job_name, notes, approved) VALUES (?, ?, ?)", (job_name, notes, approved))
        conn.commit()
        job_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        for file in request.files.getlist('videos'):
            if file.filename:
                filename = f"{job_id}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conn.execute("INSERT INTO videos (job_id, filename) VALUES (?, ?)", (job_id, filename))
                conn.commit()
        return redirect(url_for('index'))
    return render_template('add_job.html')

def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, job_name TEXT, notes TEXT, approved INTEGER DEFAULT 0)")
    conn.execute("CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY, job_id INTEGER, filename TEXT)")
    conn.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)