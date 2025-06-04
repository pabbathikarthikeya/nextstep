from flask import Flask, render_template,request,redirect,url_for,session,Response
import io
import csv
import sqlite3

app = Flask(__name__)

app.secret_key = 'f9a8b1c2d3e4f56789abcdef01234567'

@app.route("/",methods=['GET','POST'])
def home():
    if request.method=='POST':
        name=request.form['name']
        contact=request.form['contact']
        role=request.form['role']
        message=request.form['message']
        callback_needed= 1 if 'callback' in request.form else 0
        conn=sqlite3.connect('userdata.db')
        c=conn.cursor()
        c.execute('''
                    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        role TEXT,
        message TEXT,
        callback_needed INTEGER
                    )
                ''')
        c.execute("INSERT INTO users (name,contact,role,message,callback_needed) VALUES (?,?,?,?,?)",
                  (name,contact,role,message,callback_needed))
        conn.commit()
        conn.close()
        return render_template ("message.html",message="Your query is submitted")

    return render_template("index.html")
@app.route("/admin",methods=['GET','POST'])
def admin_login():
    error=None
    if request.method=='POST':
        if request.form['password']=='admin123':
            session['admin']=True
            return redirect(url_for('submissions'))
        else:
            error='Invalid password'
    return render_template("admin.html",error=error)
@app.route('/submissions')
def submissions():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn=sqlite3.connect('userdata.db')
    c=conn.cursor()
    c.execute("SELECT *FROM users")
    data=c.fetchall()
    conn.close()
    return render_template("submission.html",data=data)
@app.route('/download_csv')
def downloadcsv():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn=sqlite3.connect('userdata.db')
    c=conn.cursor()
    c.execute("SELECT *FROM users")
    data=c.fetchall()
    conn.close()

    output=io.StringIO()
    writer=csv.writer(output)
    writer.writerow(['ID', 'Name', 'Contact', 'Role', 'Message', 'Callback Needed'])
    writer.writerows(data)
    output.seek(0)
    return Response(output,
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=submissions.csv"})


if __name__ == "__main__":
    app.run(debug=True)
