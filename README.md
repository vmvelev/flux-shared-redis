# Flux Shared Redis (as a database)

### Description

This allows you to set up a redis database with master <--> replica connection to your with Flux nodes. The app will automatically check for a node that is down and change master/replicas when needed.