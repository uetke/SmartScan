""" 
    startLogbook.py
    -----------------
    This file starts a bottle server to be able to work with the lab logbook that is created while the scan2.0 program runs. 
    Even if not using Qt possibilites, web-based technologies are flexible enough in the database management. 
    Moreover it should be possible to integrate with web services as Evernote or to use it to manage larger amounts of information. 
    
    AUTHOR: Aquiles Carattino
    EMAIL: carattino@physics.leidenuniv.nl
"""
import sys
from bottle import route, run, template, install, static_file, get
import sqlite3 as lite
db='../../_private/logbook.db'
con = lite.connect(db)
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con.row_factory = dict_factory
cur = con.cursor()

# STATIC ROUTES
@get('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=sys.path[0]+"/static")  # Maybe os.path.join()?

@route('/')
def index():
    """ Displays the index page. 
    """
    return template('index')

@route('/users')
def users():
    """ Returns all the users in the database. 
    """
    sql = 'SELECT * from users'
    res = cur.execute(sql).fetchall()        
    return template('users',users=res)

@route('/setups')
def setups():
    """ Returns all the setups in the database. 
    """
    sql = 'SELECT * from setups'
    res = cur.execute(sql).fetchall()
    return template('setups',setups=res)

@route('/entries')
def entries():
    """ Returns all the entries in the database. 
    """
    sql = 'SELECT * from Logbook'
    res = cur.execute(sql).fetchall()
    
    sql = 'SELECT Id, Name from users'
    usr = cur.execute(sql).fetchall()
    
    users = {}
    for u in usr:
        users[u['Id']]=u['Name']
    
    sql = 'SELECT Id, Name from setups'
    stp = cur.execute(sql).fetchall()
    
    setups = {}
    for s in stp:
        setups[s['Id']] = s['Name']
        
    return template('entries',user=users,setup=setups,entries=res)
    
run(host='localhost', port=8080,reloader=True)
