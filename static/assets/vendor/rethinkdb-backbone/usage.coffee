Backbone = require 'backbone'

rethinkDbStore = require './rethinkdb-store'
rethinkDbStore.set(Backbone)

# setup model
UserModel = Backbone.Model.extend({
  localStorage: new Backbone.RethinkStorage(),

  defaults:
    name: no

  validate: (attrs) ->
    unless attrs.subdomain?
      "must have subdomain"
})

# Find all example
Users = Backbone.Collection.extend({
  model: UserModel,
  localStorage: new Backbone.RethinkStorage(),
})

UserSet = new Users()
UserSet.fetch(
  # callbacks
)

# Get one record
idOfRecordInDatabase = "f2581772-8cde-4f94-9aa1-3cc6c17324de"
oldRecord = new UserModel({ id: idOfRecordInDatabase})
oldRecord.fetch(
  # callbacks
)

# Create new record
paul = new UserModel({
  name: "Paul",
  what: "444444444",
})

# Save with callbacks
paul.save(
  # Parameters
  {name: "PM"},

  # Callbacks
  {
    success: (resp) ->

      # Update record in success callback
      paul.set({"name": "paul"})
      paul.save()

      paul.destroy()

    error: (model, response, options) ->
      console.log("Callback for save: Errored")
  }
)

