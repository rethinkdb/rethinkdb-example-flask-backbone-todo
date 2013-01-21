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

Open a browser: <http://localhost:5000/>

# Running #

```
python todo.py
```

# Code #

## Managing connections to RethinkDB ##

The pattern we're using for managing database connections is to have **a connection per request**. We're using Flask's `@app.before_request` and `@app.teardown_request` for opening a database connection and closing it respectively:

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

To list existing tasks, we're using as the `/todos` endpoint. We retrieve the list of existing todos using `r.table('todos')`:

```python
@app.route("/todos", methods=['GET'], defaults={'todo_id': None})
def get_todos(todo_id):
    if todo_id is None:
        selection = list(todo_table.run(g.rdb_conn))
    else:
        selection = todo_table.get(todo_id).run(g.rdb_conn)
    return json.dumps(selection)
```

## Creating a new task ##

By posting a JSON objects to `/todos` and using `todo_table.insert` we can create a new task:

```python
@app.route("/todos", methods=['POST'])
def new_todo():
    inserted = todo_table.insert(request.json).run(g.rdb_conn)
    return jsonify(id=inserted['generated_keys'][0])
```

The `insert` operation returns a single object 

## Retrieving a single task ##

Every task has a unique id allowing us to retrieve a . 

```
@app.route("/todos", methods=['GET'], defaults={'todo_id': None})
def get_todos(todo_id):
    if todo_id is None:
        selection = list(todo_table.run(g.rdb_conn))
    else:
        selection = todo_table.get(todo_id).run(g.rdb_conn)
    return json.dumps(selection)
```

Using a task's ID will prove more useful when updating, marking as complete, or deleting it.

## Editing a task ##

Updating a task is performed on a `PUT` request. To save the change we'll do a `replace`:

```python
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).replace(request.json).run(g.rdb_conn))
```


If you'd like the update operation to be a `PATCH`, you can use instead `update` for saving the merged data:

```python
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).replace(request.json).run(g.rdb_conn))
```

## Marking a task as completed ##

Marking a task as completed is similar to editing it. The updated version with the `done` attribute turned on replaces the older version:

```python
@app.route("/todos/<string:todo_id>", methods=['PUT'])
def update_todo(todo_id):
    return jsonify(todo_table.get(todo_id).replace(request.json).run(g.rdb_conn))
```

## Deleting a task ##

For deleting a task we'll trigger a database `delete` operation upon a `DELETE /todos/<ID>` request:

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

*   **Using a connection per request**
*   **Batched iterators**

