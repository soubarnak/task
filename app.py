from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)  # Non-required end date
    assigned_to = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    completion_date = db.Column(db.Date, nullable=True)

# Route to display all tasks
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# Route to add a task
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form.get('description', '')
    start_date = request.form['start_date']
    end_date = request.form.get('end_date', None)  # Optional end date
    assigned_to = request.form['assigned_to']
    status = request.form['status']
    
    new_task = Task(
        title=title,
        description=description,
        start_date=datetime.strptime(start_date, '%Y-%m-%d'),
        end_date=datetime.strptime(end_date, '%Y-%m-%d') if end_date else None,
        assigned_to=assigned_to,
        status=status
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

# Route to update a task
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description', '')
        task.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        task.end_date = datetime.strptime(request.form.get('end_date', ''), '%Y-%m-%d') if request.form.get('end_date') else None
        task.assigned_to = request.form['assigned_to']
        task.status = request.form['status']
        task.completion_date = datetime.strptime(request.form.get('completion_date', ''), '%Y-%m-%d') if request.form.get('completion_date') else None
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', task=task)

# Route to delete a task
@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# Route to generate a report
@app.route('/report')
def report():
    tasks = Task.query.all()
    report_data = []
    for task in tasks:
        if task.completion_date:
            time_taken = (task.completion_date - task.start_date).days  # Time taken from start to completion
        else:
            time_taken = None
        report_data.append({
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'assigned_to': task.assigned_to,
            'start_date': task.start_date,
            'end_date': task.end_date,
            'completion_date': task.completion_date,
            'time_taken': time_taken
        })
    return render_template('report.html', report_data=report_data)

# Create the database and tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
