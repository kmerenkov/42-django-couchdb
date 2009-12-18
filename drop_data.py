#!/usr/bin/python
from couchdb import Server


s = Server('http://localhost:5984/')
for db in s:
    print "Dropping %s..." % db
    del s[db]
