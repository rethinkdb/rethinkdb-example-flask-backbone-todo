# What is it #

A demo web application in the spirit of TodoMVC showing how to use RethinkDB as a backend for Flask applications.

As any todo application, this one implements the following functionality:

1. list existing tasks
2. retrieve a single task
2. create new task
3. edit a task
4. mark a task as done or incomplete 
5. delete a task
6. mark all tasks as completed

One missing feature we've left out as an exercise is making this Flask todo app force  users to complete their tasks. In time.

# Complete stack #

*   Flask
*   Backbone
*   RethinkDB
*   ...

# Installation #

```
git clone git://github.com/rethinkdb/rethinkdb-example-flask-backbone-todo.git
pip install Flask
pip install rethinkdb
```

_Note_: If you don't have RethinkDB installed, you can follow these instructions to get it up and running. For this demo we'll also need to create a new database and table.

# Running #

```
python todo.py
```

# Code #

## Managing connections to RethinkDB ##

The pattern we're using for managing database connections is to use a connection per request. We're using Flask's `@app.before_request` and `@app.teardown_request` for opening a database connection and closing it respectively:

```
code
``` 

## Listing existing todos ##

To list existing tasks, we're using as the `/todos` endpoint. We retrieve the list of existing todos using `r.table('todos')`:

```
code
```

## Retrieving a single task ##

Every task has a unique id allowing us to retrieve a . 
```
code
```

Using a task's ID will prove more useful when updating, marking as complete, or deleting it.

## Editing a task ##

Updating a task is performed on a `PUT` request. To save the change we'll do a `replace`:

```
code
```


If you'd like the update operation to be a `PATCH`, you can use instead `update` for saving the merged data:

```
code
```

## Marking a task as completed ##

Marking a task as completed is similar to editing it. The updated version with the `done` attribute turned on replaces the older version:

```
code
```

## Deleting a task ##

For deleting a task we'll trigger a database `delete` operation upon a `DELETE /todos/<ID>` request:

```
code
```

## Marking all tasks as completed ##

There are two ways to mark all tasks as completed. The simple approach is to iterate over the tasks and mark them one by one:

```

A different way to implement this is by submitting a special `PUT` request and then performing a bulk update on the database:

```
code
```

#  #

