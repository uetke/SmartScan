# Collection of functions for keeping an electronic lab logbook in an sqlite database
import sys
import os
import sqlite3 as lite
from datetime import datetime
from lib.logger import logger

class db_comm():
    """ Class for adding and editing entries to a database storing information
        on the experiments run, by whom, etc.
    """
    def __init__(self, db='../_private/logbook.db'):
        """ Initializes the connection to the database. 
            It takes one argument, the location of the database
        """
        if not os.path.exists(db):
            print('Database does not exist')
        self.con = lite.connect(db)
        self.cur = self.con.cursor()
        self.sync_schema()
    
    def create_database(self):
        """ Function for creating the database. 
            It easily deletes the previous database. Use with CARE.
        """

        sql = "CREATE TABLE IF NOT EXISTS Users(Id INTEGER PRIMARY KEY, Name TEXT, Date TEXT)"
        self.cur.execute(sql)
        
        sql = """CREATE TABLE IF NOT EXISTS Logbook (Id INTEGER PRIMARY KEY, Date TEXT, User INTEGER,
            Entry TEXT, File TEXT, Detectors TEXT, Variables TEXT, Setup INTEGER, Comments TEXT)"""
        
        self.cur.execute(sql)
        
        sql = "CREATE TABLE IF NOT EXISTS Setups(Id INTEGER PRIMARY KEY, Name TEXT, Date TEXT, Description TEXT, File TEXT)"
        self.cur.execute(sql)
        self.con.commit()
        
        return True

    def _update_database(self, tblmask):
        if tblmask & 1:
            self.cur.execute("""CREATE TABLE IF NOT EXISTS metadata (
                entry_id INTEGER, 
                component TEXT,
                key TEXT,
                value TEXT)""")
            self.con.commit()

    def sync_schema(self):
        mylogger = logger()

        tables = [row[0] for row in  self.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if 'Users' not in tables:
            mylogger.info('Creating database tables.')
            self.create_database()
        if 'metadata' not in tables:
            mylogger.info('Upgrading database.')
            self._update_database(1)

        
    def new_user(self, user):
        """ Creates a new user.
            Returns the ID of the newly created user.
        """
        sql = "INSERT INTO Users (Name, Date) VALUES (?, ?)"
        self.cur.execute(sql, (user['name'], self.now()))
        self.con.commit()
        return self.cur.lastrowid
    
    def new_setup(self, setup):
        """ Creates a new setup. 
            Returns the ID of the newly created setup.
        """
        sql = "INSERT INTO Setups (Date, Name, Description, File) VALUES (?, ?, ?, ?)"
        self.cur.execute(sql,(self.now(),setup['name'],setup['description'],setup['file']))
        self.con.commit()
        return self.cur.lastrowid
    
    def new_entry(self, entry):
        """ Creates a new entry in the logbook. 
            Returns the ID of the newly created entry. 
        """
        sql = """INSERT INTO Logbook (DATE, User, Entry, File, Detectors, Variables, Setup, Comments)
            values (?,?,?,?,?,?,?,?)"""
        self.cur.execute(sql,(self.now(),entry['user'],entry['entry'],entry['file'],entry['detectors'],
                              entry['variables'],entry['setup'],entry['comments']))
        self.con.commit()
        return self.cur.lastrowid

    def update_entry(self, rowid, entry):
        sql = """UPDATE Logbook SET date=?, user=?, entry=?, file=?,
                                    detectors=?, variables=?, setup=?, comments=?
                        WHERE id=?"""
        self.cur.execute(sql, (self.now(), entry['user'], entry['entry'], entry['file'],
                               entry['detectors'], entry['variables'], entry['setup'],
                               entry['comments'], rowid))
        self.con.commit()
        return rowid

    def add_metadata_to_entry(self, entry_id, component, key, value):
        sql = """INSERT INTO metadata (entry_id, component, key, value) VALUES (?,?,?,?)"""
        self.cur.execute(sql,(entry_id, component, key, value))
        self.con.commit()
        return self.cur.lastrowid

    
    def get_users(self):
        """ Returns a list of all current users and their IDs. 
        """
        sql = 'SELECT Id, Name from Users'
        self.cur.execute(sql)
        return self.cur.fetchall()
    
    def get_setups(self):
        """ Returns a list of all current setups and their IDs. 
        """
        sql = 'SELECT Id, Description from Setups'
        self.cur.execute(sql)
        return self.cur.fetchall()
    
    def get_entries(self):
        """ Returns a list of all the entries in the logbook. 
        """
        sql = 'SELECT Id, DATE, User, Entry, File, Detectors, Variables, Setup, Comments from Logbook'
        self.cur.execute(sql)
        return self.cur.fetchall()
    
    def now(self):
        """ Returns the date formatted in a particular way to have entries
            consistent with each other. 
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def run_sql(self,sql):
        """ Runs arbitrary SQL code, for debugging purposes. 
        """
        self.cur.execute(sql)
        return self.cur.fetchall()
        
    
    def __del__(self):
        self.con.close()

if __name__ == "__main__":
    db = db_comm()
    db.cur.execute('SELECT SQLITE_VERSION()')
    data = db.cur.fetchone()
    print("SQLite3 version %s" % (data))
            
