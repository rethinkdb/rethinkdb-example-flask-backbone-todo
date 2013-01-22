# What is it #

A demo web application in the spirit of [TodoMVC](http://addyosmani.github.com/todomvc/) showing how to use **RethinkDB as a backend for Flask applications**.

As any todo application, this one implements the following functionality:

1. [managing database connections](#managing-connections-to-rethinkdb)
1. [list existing tasks](#listing-existing-todos)
2. [retrieve a single task](#retrieving-a-single-task)
3. [create new task](#creating-a-task)
4. [edit a task](#editing-a-task)
5. [mark a task as done or incomplete](#marking-a-task-as-completed)
6. [delete a task](#deleting-a-task)
7. [mark all tasks as completed](#marking-all-tasks-as-completed)

One missing feature we've left out as an exercise is making this Flask todo app force  users to complete their tasks. In time.

# Complete stack #

*   [Flask](http://flask.pocoo.org)
*   [Backbone](http://backbonejs.org)
*   [RethinkDB](http://www.rethinkdb.com)

# Installation #

```
git clone git://github.com/rethinkdb/rethinkdb-example-flask-backbone-todo.git
pip install Flask
pip install rethinkdb
```

_Note_: If you don't have RethinkDB installed, you can follow [these instructions to get it up and running](http://www.rethinkdb.com/docs/install/). For this demo we'll use the default database `test` and a table named `todos`. You can create the table directly from the RethinkDB Admin UI.

# Running the application #

Flask provides an easy way to test your application:

```
python todo.py
```

Then open a browser: <http://localhost:5000/>


# Code #

## Managing connections to RethinkDB ##

The pattern we're using for managing database connections is to have **a connection per request**. We're using Flask's `@app.before_request` and `@app.teardown_request` for [opening a database connection](http://www.rethinkdb.com/api/#py:accessing_rql-connect) and [closing it](http://www.rethinkdb.com/api/#py:accessing_rql-close) respectively:

```python
@app.before_request
def before_request():
    # Connect to the RethinkDB database. 
    # We attach it to the flask.g object, which is only attached to the active request and 
    # will ensure we use different connections for simulataneous requests
    g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT)
    
@app.teardown_request
def teardown_request(exception):
    # Close the connection after each request has completed.
    g.rdb_conn.close()
``` 



## Listing existing todos ##

To list existing tasks, we are using `r.table('todos') in response to a GET request`:

```python
@app.route("/todos", methods=['GET'], defaults={'todo_id': None})
def get_todos(todo_id):
	...
    selection = list(todo_table.run(g.rdb_conn))
    return json.dumps(selection)
```

In RethinkDB, the shortcut `table.run(connection)` returns a batched iterator over all rows in the table.

## Creating a new task ##

We will create a new task in response to a POST request to `/todos` with a JSON payload using [`table.insert`](http://www.rethinkdb.com/api/#py:writing_data-insert):

```python
@app.route("/todos", methods=['POST'])
def new_todo():
    inserted = todo_table.insert(request.json).run(g.rdb_conn)
    return jsonify(id=inserted['generated_keys'][0])
```

The `insert` operation returns a single object specifying the number of successfully created objects and their corresponding IDs:

```javascript
{
	"inserted": 1 ,
	"errors": 0 ,
	"generated_keys": ["773666ac-841a-44dc-97b7-b6f3931e9b9f"]
}
```

## Retrieving a single task ##

When creating a new task, each gets assigned an unique ID. Then we could retrieve a specific task by GETing `/todos/<todo_id>`. The corresponding Re

```
@app.route("/todos", methods=['GET'], defaults={'todo_id': None})
def get_todos(todo_id):
	...
	selection = todo_table.get(todo_id).run(g.rdb_conn)
	return json.dumps(selection)
```

Using a task's ID will prove more useful when updating, marking as complete, or deleting it.

## Editing a task ##

Updating a task is performed on a `PUT` request. To save the change we'll do a [`replace`](http://www.rethinkdb.com/api/#py:writing_data-replace):

```python
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).replace(request.json).run(g.rdb_conn))
```

If you'd like the update operation to happen as the result of a `PATCH` request (carrying only the updated fields), you can use instead [`update`](http://www.rethinkdb.com/api/#py:writing_data-update) for saving the merged data:

```python
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).update(request.json).run(g.rdb_conn))
```

Both `replace` and `update` operations can be run against multiple rows.

## Marking a task as completed ##

Marking a task as completed is similar to editing it. The updated version with the `done` attribute turned on [replaces](http://www.rethinkdb.com/api/#py:writing_data-replace) the older version:

```python
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).replace(request.json).run(g.rdb_conn))
```

## Deleting a task ##

For deleting a task we'll trigger a database [`delete`](http://www.rethinkdb.com/api/#py:writing_data-delete) operation on a `DELETE /todos/<todo_id>` request:

```python
@app.route("/todos/<string:todo_id>", methods=['DELETE'])
def delete_todo(todo_id):
    return jsonify(todo_table.get(todo_id).delete().run(g.rdb_conn))
```

## Marking all tasks as completed ##

There are two ways to mark all tasks as completed. The simple approach is to iterate over the tasks and [mark them one by one](#marking-a-task-as-completed). The downside of this approach is the number of requests sent to the server. 

A different way to implement this is by submitting a special `PUT` request and then performing a bulk update on the database. For example:

```
@app.route("/todos", methods=['PUT'])
def update_all():
	request.args.get('key', '')
	todo_table.update({'done: True})
```

# Best practices #

*   **Managing connections: a connection per request**

	The RethinkDB server doesn't use a thread-per-connnection approach so opening connections per request will not slow down your database.
	
*   **Fetching multiple rows: batched iterators**

	When fetching multiple rows from a table, RethinkDB returns a batched iterator containing initially a subset of the complete result. Once the end of the current batch was reached, a new batch is retrieved from the server. Anyways from a coding point of view this is transparent:
	
	```python
	for result in r.table('todos').run(g.rdb_conn):
		print result
	```
	
*	`replace` vs `update`

	Both `replace` and `update` operations can be used to modify a single row or multiple row. Their behavior is different though: `replace` will completely replace the existing rows

# License #

This demo application is licensed under the MIT license: <http://opensource.org/licenses/mit-license.php>
