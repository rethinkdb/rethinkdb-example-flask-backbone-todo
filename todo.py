from flask import Flask, g, jsonify, render_template, request
import json
from rethinkdb import r

# We specify the connection details and create todo_table, a reference to the table we'll be using to store todos
RDB_HOST = 'localhost'
RDB_PORT = 28015
todo_table = r.table('todos')

app = Flask(__name__)
app.config.from_object(__name__)

@app.before_request
def before_request():
    # Connect to the RethinkDB database. We attach it to the flask.g object, which is only attached to the active request and will ensure we use different connections for simulataneous requests
    g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT)

@app.teardown_request
def teardown_request(exception):
    # Close the connection after each request has completed.
    g.rdb_conn.close()

@app.route("/")
def show_todos():
    return render_template('todo.html')

# Fetching all todos (or a specific todo)
@app.route("/todos", methods=['GET'], defaults={'todo_id': None})
@app.route("/todos/<string:todo_id>", methods=['GET'])
def get_todos(todo_id):
    if todo_id is None:
        selection = list(todo_table.run(g.rdb_conn))
    else:
        selection = todo_table.get(todo_id).run(g.rdb_conn)
    return json.dumps(selection)

# Creating a new todo
@app.route("/todos", methods=['POST'])
def new_todo():
    inserted = todo_table.insert(request.json).run(g.rdb_conn)
    return jsonify(id=inserted['generated_keys'][0])

# Updating an existing todo
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).replace(request.json).run(g.rdb_conn))

# Deleting a todo
@app.route("/todos/<string:todo_id>", methods=['DELETE'])
def delete_todo(todo_id):
    return jsonify(todo_table.get(todo_id).delete().run(g.rdb_conn))

if __name__ == "__main__":
    app.run(debug=True)
