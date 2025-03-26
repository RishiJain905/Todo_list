from flask import render_template, url_for, redirect, g, abort, request
from app import app
from app.forms import TaskForm
from rethinkdb import r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

# RethinkDB configuration
RDB_HOST = 'localhost'
RDB_PORT = 28015
TODO_DB = 'todo'

# Database setup; only run once
def dbSetup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_create(TODO_DB).run(connection)
        r.db(TODO_DB).table_create('todos').run(connection)
        print('Database setup completed')
    except RqlRuntimeError:
        print('Database already exists.')
    finally:
        connection.close()

dbSetup()

@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT, db=TODO_DB)
    except RqlDriverError:
        abort(503, "Database connection could not be established.")

@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TaskForm()
    if form.validate_on_submit():
        r.table('todos').insert({"name": form.label.data}).run(g.rdb_conn)
        return redirect(url_for('index'))
    tasks = list(r.table('todos').run(g.rdb_conn))
    return render_template('index.html', form=form, tasks=tasks)

@app.route('/delete/<string:task_id>', methods=['POST'])
def delete_task(task_id):
    try:
        r.table('todos').get(task_id).delete().run(g.rdb_conn)
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error deleting task: {e}")
        abort(500, "An error occurred while deleting the task.")

@app.route('/update/<string:task_id>', methods=['POST'])
def update_task(task_id):
    try:
        new_name = request.form.get('name')
        if not new_name:
            abort(400, "Task name is required.")
        r.table('todos').get(task_id).update({"name": new_name}).run(g.rdb_conn)
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error updating task: {e}")
        abort(500, "An error occurred while updating the task.")
