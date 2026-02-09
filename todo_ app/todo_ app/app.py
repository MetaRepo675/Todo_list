from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
from models import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # در پروژه واقعی از environment variable استفاده کنید

# مقداردهی اولیه دیتابیس
init_db()

@app.route('/')
def index():
    """صفحه اصلی نمایش وظایف"""
    conn = get_db_connection()
    
    # پارامترهای فیلتر
    filter_completed = request.args.get('filter')
    
    if filter_completed == 'completed':
        todos = conn.execute(
            'SELECT * FROM todos WHERE completed = 1 ORDER BY priority DESC, created_at DESC'
        ).fetchall()
    elif filter_completed == 'pending':
        todos = conn.execute(
            'SELECT * FROM todos WHERE completed = 0 ORDER BY priority DESC, created_at DESC'
        ).fetchall()
    else:
        todos = conn.execute(
            'SELECT * FROM todos ORDER BY completed, priority DESC, created_at DESC'
        ).fetchall()
    
    conn.close()
    return render_template('index.html', todos=todos, filter_completed=filter_completed)

@app.route('/add', methods=['POST'])
def add_todo():
    """افزودن وظیفه جدید"""
    task = request.form['task']
    description = request.form.get('description', '')
    priority = int(request.form.get('priority', 1))
    due_date = request.form.get('due_date')
    
    if not task:
        flash('عنوان وظیفه نمی‌تواند خالی باشد', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO todos (task, description, priority, due_date) VALUES (?, ?, ?, ?)',
        (task, description, priority, due_date)
    )
    conn.commit()
    conn.close()
    
    flash('وظیفه با موفقیت اضافه شد', 'success')
    return redirect(url_for('index'))

@app.route('/complete/<int:todo_id>')
def complete_todo(todo_id):
    """تکمیل کردن یک وظیفه"""
    conn = get_db_connection()
    conn.execute('UPDATE todos SET completed = 1 WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    
    flash('وظیفه به عنوان تکمیل شده علامت گذاری شد', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    """حذف یک وظیفه"""
    conn = get_db_connection()
    conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    
    flash('وظیفه با موفقیت حذف شد', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    """ویرایش یک وظیفه"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        task = request.form['task']
        description = request.form.get('description', '')
        priority = int(request.form.get('priority', 1))
        due_date = request.form.get('due_date')
        
        if not task:
            flash('عنوان وظیفه نمی‌تواند خالی باشد', 'error')
            return redirect(url_for('edit_todo', todo_id=todo_id))
        
        conn.execute(
            '''UPDATE todos 
               SET task = ?, description = ?, priority = ?, due_date = ? 
               WHERE id = ?''',
            (task, description, priority, due_date, todo_id)
        )
        conn.commit()
        conn.close()
        
        flash('وظیفه با موفقیت ویرایش شد', 'success')
        return redirect(url_for('index'))
    
    # GET request
    todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    conn.close()
    
    if todo is None:
        flash('وظیفه پیدا نشد', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit.html', todo=todo)

@app.route('/toggle_priority/<int:todo_id>')
def toggle_priority(todo_id):
    """تغییر اولویت یک وظیفه"""
    conn = get_db_connection()
    todo = conn.execute('SELECT priority FROM todos WHERE id = ?', (todo_id,)).fetchone()
    
    if todo:
        new_priority = 2 if todo['priority'] == 1 else 1
        conn.execute('UPDATE todos SET priority = ? WHERE id = ?', (new_priority, todo_id))
        conn.commit()
    
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
