# A demo web application in the spirit of
# [TodoMVC](http://addyosmani.github.com/todomvc/) showing how to use
# **RethinkDB as a backend for Flask and Backbone.js applications**.
#
# For details about the complete stack, installation, and running the
# app see the
# [README](https://github.com/rethinkdb/rethinkdb-example-flask-backbone-todo).
import argparse
import json
import os

from flask import Flask, g, jsonify, render_template, request, abort

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

#### Connection details

# We will use these settings later in the code to connect to the
# RethinkDB server.
RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
TODO_DB = 'todoapp'

#### Setting up the app database

# The app will use a table `todos` in the database specified by the
# `TODO_DB` variable.  We'll create the database and table here using
# [`db_create`](http://www.rethinkdb.com/api/python/db_create/)
# and
# [`table_create`](http://www.rethinkdb.com/api/python/table_create/) commands.
def dbSetup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_create(TODO_DB).run(connection)
        r.db(TODO_DB).table_create('todos').run(connection)
        print 'Database setup completed. Now run the app without --setup.'
    except RqlRuntimeError:
        print 'App database already exists. Run the app without --setup.'
    finally:
        connection.close()


app = Flask(__name__)
app.config.from_object(__name__)

#### Managing connections

# The pattern we're using for managing database connections is to have **a connection per request**. 
# We're using Flask's `@app.before_request` and `@app.teardown_request` for 
# [opening a database connection](http://www.rethinkdb.com/api/python/connect/) and 
# [closing it](http://www.rethinkdb.com/api/python/close/) respectively.
@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT, db=TODO_DB)
    except RqlDriverError:
        abort(503, "No database connection could be established.")

@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass


#### Listing existing todos

# To retrieve all existing tasks, we are using
# [`r.table`](http://www.rethinkdb.com/api/python/table/)
# command to query the database in response to a GET request from the
# browser. When `table(table_name)` isn't followed by an additional
# command, it returns all documents in the table.
#    
# Running the query returns an iterator that automatically streams
# data from the server in efficient batches.
@app.route("/todos", methods=['GET'])
def get_todos():
    selection = list(r.table('todos').run(g.rdb_conn))
    return json.dumps(selection)

#### Creating a todo

# We will create a new todo in response to a POST request to `/todos`
# with a JSON payload using
# [`table.insert`](http://www.rethinkdb.com/api/python/insert/).
#
# The `insert` operation returns a single object specifying the number
# of successfully created objects and their corresponding IDs:
# 
# ```
# {
#   "inserted": 1,
#   "errors": 0,
#   "generated_keys": [
#     "773666ac-841a-44dc-97b7-b6f3931e9b9f"
#   ]
# }
# ```

@app.route("/todos", methods=['POST'])
def new_todo():
    inserted = r.table('todos').insert(request.json).run(g.rdb_conn)
    return jsonify(id=inserted['generated_keys'][0])


#### Retrieving a single todo

# Every new task gets assigned a unique ID. The browser can retrieve
# a specific task by GETing `/todos/<todo_id>`. To query the database
# for a single document by its ID, we use the
# [`get`](http://www.rethinkdb.com/api/python/get/)
# command.
#
# Using a task's ID will prove more useful when we decide to update
# it, mark it completed, or delete it.
@app.route("/todos/<string:todo_id>", methods=['GET'])
def get_todo(todo_id):
    todo = r.table('todos').get(todo_id).run(g.rdb_conn)
    return json.dumps(todo)

#### Editing/Updating a task

# Updating a todo (editing it or marking it completed) is performed on
# a `PUT` request.  To save the updated todo we'll do a
# [`replace`](http://www.rethinkdb.com/api/python/replace/).
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(r.table('todos').get(todo_id).replace(request.json)
                    .run(g.rdb_conn))

# If you'd like the update operation to happen as the result of a
# `PATCH` request (carrying only the updated fields), you can use the
# [`update`](http://www.rethinkdb.com/api/python/update/)
# command, which will merge the JSON object stored in the database
# with the new one.
@app.route("/todos/<string:todo_id>", methods=['PATCH'])
def patch_todo(todo_id):
    return jsonify(r.table('todos').get(todo_id).update(request.json)
                    .run(g.rdb_conn))


#### Deleting a task

# To delete a todo item we'll call a
# [`delete`](http://www.rethinkdb.com/api/python/delete/)
# command on a `DELETE /todos/<todo_id>` request.
@app.route("/todos/<string:todo_id>", methods=['DELETE'])
def delete_todo(todo_id):
    return jsonify(r.table('todos').get(todo_id).delete().run(g.rdb_conn))

@app.route("/")
def show_todos():
    return render_template('todo.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask todo app')
    parser.add_argument('--setup', dest='run_setup', action='store_true')

    args = parser.parse_args()
    if args.run_setup:
        dbSetup()
    else:
        app.run(debug=True)


# ### Best practices ###
#
# #### Managing connections: a connection per request ####
#
# The RethinkDB server doesn't use a thread-per-connnection approach
# so opening connections per request will not slow down your database.
# 
# #### Fetching multiple rows: batched iterators ####
#
# When fetching multiple rows from a table, RethinkDB returns a
# batched iterator initially containing a subset of the complete
# result. Once the end of the current batch is reached, a new batch is
# automatically retrieved from the server. From a coding point of view
# this is transparent:
#   
#     for result in r.table('todos').run(g.rdb_conn):
#         print result
#     
#    
# #### `replace` vs `update` ####
#
# Both `replace` and `update` operations can be used to modify one or
# multiple rows. Their behavior is different:
#    
# *   `replace` will completely replace the existing rows with new values
# *   `update` will merge existing rows with the new values


#
# Licensed under the MIT license: <http://opensource.org/licenses/mit-license.php>
#
# Copyright (c) 2012 RethinkDB
#
