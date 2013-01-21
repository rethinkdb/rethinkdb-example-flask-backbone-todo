_ = require("underscore")
{inspect} = require('util')

logDebug = false
dbQueries = true

# Datastore

logMessage = (method, tableName, model) ->
  "\t" + method + ": '" + model.tableName + "' => " + inspect(model.attributes)

set = (Backbone) ->
  Backbone.RethinkStorage = ->

  _.extend(Backbone.RethinkStorage.prototype, {
    create: (conn, model, callback) ->
      console.log(logMessage("create", model.tableName, model)) if dbQueries
      cur = conn.run(model.tableCur().insert(model.attributes))
      cur.next (insertData) ->
        console.log("Inserted: ", model.tableName, insertData) if dbQueries
        if insertData.generated_keys && insertData.generated_keys.length > 0
          model.set("id", insertData.generated_keys[0])
          callback(model)
        else
          callback(model)

    update: (conn, model, callback) ->
      console.log(logMessage("update", model.tableName, model)) if dbQueries
      cur = conn.run(model.tableCur().get(model.id).update(model.attributes))
      cur.next (updateData) ->
        callback(model.toJSON())

    findAll: (conn, model, callback) ->
      console.log(logMessage("findAll", model.tableName, model)) if dbQueries
      cur = conn.run(model.tableCur())
      cur.collect (docs) ->
        console.log("found docs") if logDebug
        console.log(docs) if logDebug
        callback(docs)

    find: (conn, model, callback) ->
      console.log(logMessage("find", model.tableName, model)) if dbQueries
      idAttribute = model.idAttribute || "id"
      cur = conn.run(model.tableCur().get(model.id, idAttribute))
      cur.collect (docs) ->
        console.log("found doc") if logDebug
        console.log(docs) if logDebug
        if docs.length > 0
          doc = docs[0]
          callback(doc)
        else
          callback null

    "delete": (conn, model, callback) ->
      console.log(logMessage("delete", model.tableName, model)) if dbQueries
      cur = conn.run(model.tableCur().get(model.id).del())
      cur.collect (deleteResponse) ->
        callback(deleteResponse)
  })

  Backbone.sync = (method, model, options, error) ->
    console.log("backbone sync: " + method) if logDebug
    store = model.localStorage

    conn = options.conn
    console.log("conn", conn) if logDebug

    code = (resp) ->
      if (resp)
        options.success(resp)
      else
        options.error(resp)

    switch method
      when "create"
        store.create conn, model, code
      when "update"
        store.update conn, model, code
      when "read"
        if model.id?
          store.find conn, model, code
        else
          store.findAll conn, model, code
      when "delete"
        store.delete conn, model, code

exports.set = set
