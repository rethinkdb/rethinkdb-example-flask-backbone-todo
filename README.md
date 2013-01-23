# What is it #

A demo web application in the spirit of [TodoMVC](http://addyosmani.github.com/todomvc/) showing how to use **RethinkDB as a backend for Flask applications**.

As any todo application, this one implements the following functionality:

1. [managing database connections](#section-Managing_connections)
2. [list existing todos](#section-Listing_existing_todos)
3. [create new todo](#section-Creating_a_todo)
4. [retrieve a single todo](#section-Retrieving_a_single_todo)
5. [edit a todo or mark a todo as done](#section-Editing/Updating_a_todo)
6. [delete a todo](#section-Deleting_a_todo)

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

_Note_: If you don't have RethinkDB installed, you can follow [these instructions to get it up and running](http://www.rethinkdb.com/docs/install/). 

# Running the application #

Firstly we'll need to create the database `todoapp` and the table used by this app: `todos`. You can
do this by running:

```
python todo.py --setup
```

Flask provides an easy way to run the app:

```
python todo.py
```

Then open a browser: <http://localhost:5000/>.


# Annotated Source Code #

After checking out the code, you can also read the annotated source [here][]

# License #

This demo application is licensed under the MIT license: <http://opensource.org/licenses/mit-license.php>
