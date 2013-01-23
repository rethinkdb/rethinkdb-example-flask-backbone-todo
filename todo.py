#
# A demo web application in the spirit of [TodoMVC](http://addyosmani.github.com/todomvc/) showing how to use **RethinkDB as a backend for Flask applications**.
#
# For details about the complete stack, installation, and running see the [README](https://github.com/rethinkdb/rethinkdb-example-flask-backbone-todo).
#
from flask import Flask, g, jsonify, render_template, request
import json
from rethinkdb import r

# RethinkDB connection details:
RDB_HOST = 'localhost'
RDB_PORT = 28015

#### Setting up the app database

# The app will use a table `todos` in the `todoapp` database. 
# We'll create these here using [`db_create`](http://www.rethinkdb.com/api/#py:manipulating_databases-db_create)
# and [`table_create`](http://www.rethinkdb.com/api/#py:manipulating_tables-table_create).
def setup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    connection.run(r.db_create('todoapp'))
    connection.run(r.db('todoapp').table_create('todos'))

# We keep a reference to the `todos` table as we'll use it everywhere:
todo_table = r.db('todoapp').table('todos')

app = Flask(__name__)
app.config.from_object(__name__)


#### Managing connections

# The pattern we're using for managing database connections is to have **a connection per request**. 
# We're using Flask's `@app.before_request` and `@app.teardown_request` for 
# [opening a database connection](http://www.rethinkdb.com/api/#py:accessing_rql-connect) and 
# [closing it](http://www.rethinkdb.com/api/#py:accessing_rql-close) respectively.
@app.before_request
def before_request():
    g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT)

@app.teardown_request
def teardown_request(exception):
    g.rdb_conn.close()


#### Listing existing todos

# To retrieve all existing tasks, we are using [`r.table('todos')`](http://www.rethinkdb.com/api/#py:selecting_data-table) 
# in response to a GET request. `table.run()` returns a batched iterator that we transform into a `list`.
@app.route("/todos", methods=['GET'])
def get_todos():
    selection = list(todo_table.run(g.rdb_conn))
    return json.dumps(selection)

#### Creating a todo

# We will create a new todo in response to a POST request to `/todos` with a JSON payload 
# using [`table.insert`](http://www.rethinkdb.com/api/#py:writing_data-insert).
#
# The `insert` operation returns a single object specifying the number of successfully created objects and their corresponding IDs: 
# `{ "inserted": 1,  "errors": 0,  "generated_keys": ["773666ac-841a-44dc-97b7-b6f3931e9b9f"] }`
@app.route("/todos", methods=['POST'])
def new_todo():
    inserted = todo_table.insert(request.json).run(g.rdb_conn)
    return jsonify(id=inserted['generated_keys'][0])


#### Retrieving a single todo

# When creating a new task, each gets assigned an unique ID. Then we could retrieve a specific task by GETing `/todos/<todo_id>`. 
# For accessing a single row by its id we use [`table.get`](http://www.rethinkdb.com/api/#py:selecting_data-get).
#
# Using a task's ID will prove more useful when updating, marking as complete, or deleting it.
@app.route("/todos/<string:todo_id>", methods=['GET'])
def get_todos(todo_id):
    todo = todo_table.get(todo_id).run(g.rdb_conn)
    return json.dumps(todo)

#### Editing/Updating a task

# Updating a todo (editing it or marking it as completed) is performed on a `PUT` request. 
# To save the updated todo we'll do a [`replace`](http://www.rethinkdb.com/api/#py:writing_data-replace).
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).replace(request.json).run(g.rdb_conn))

# If you'd like the update operation to happen as the result of a `PATCH` request (carrying only the updated fields), 
# you can use instead [`update`](http://www.rethinkdb.com/api/#py:writing_data-update) 
# which will merge the database stored JSON object with the new one.
@app.route("/todos/<string:todo_id>", methods=['PATCH'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).update(request.json).run(g.rdb_conn))


#### Deleting a task

# For deleting a todo we'll trigger a database [`delete`](http://www.rethinkdb.com/api/#py:writing_data-delete) 
# on a `DELETE /todos/<todo_id>` request.
@app.route("/todos/<string:todo_id>", methods=['DELETE'])
def delete_todo(todo_id):
    return jsonify(todo_table.get(todo_id).delete().run(g.rdb_conn))

@app.route("/")
def show_todos():
    return render_template('todo.html')


if __name__ == "__main__":
    app.run(debug=True)


# ## Best practices ##
#
# **Managing connections: a connection per request**
#
# The RethinkDB server doesn't use a thread-per-connnection approach so opening connections per request will not slow down your database.
#    
# **Fetching multiple rows: batched iterators**
#
# When fetching multiple rows from a table, RethinkDB returns a batched iterator containing initially a subset of the complete result. 
# Once the end of the current batch is reached, a new batch is retrieved from the server. From a coding point of view this is transparent:
#   
#     for result in r.table('todos').run(g.rdb_conn):
#         print result
#     
#    
# **`replace` vs `update`**
#
# Both `replace` and `update` operations can be used to modify one or multiple rows. Their behavior is different: 
#    
# *   `replace` will completely replace the existing rows with new values
# *   `update` will merge existing rows with the new values


#
# Licensed under the MIT license: <http://opensource.org/licenses/mit-license.php>
#
# Copyright (c) 2012 RethinkDB
#