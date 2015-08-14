# Collection of functions for keeping an electronic lab logbook in an sqlite database
import sys
import os
import sqlite3 as lite
from datetime import datetime

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
        else:
            self.con = lite.connect(db)
            self.cur = self.con.cursor()
    
    def create_database(self):
        """ Function for creating the database. 
            It easily deletes the previous database. Use with CARE.
        """

        sql = "CREATE TABLE Users(Id INTEGER PRIMARY KEY, Name TEXT, Date TEXT)"
        self.cur.execute(sql)
        
        sql = "CREATE TABLE Logbook (Id INTEGER PRIMARY KEY, Date TEXT, User INTEGER,\
            Entry TEXT, File TEXT, Detectors TEXT, Variables TEXT, Setup INTEGER, Comments TEXT) "
        
        self.cur.execute(sql)
        
        sql = "CREATE TABLE Setup(Id INTEGER PRIMARY KEY, Date TEXT, Description TEXT, File TEXT)"
        self.cur.execute(sql)
        self.con.commit()
        
        sql = "CREATE TABLE Last_Settings(Id INTEGER PRIMARY KEY, "
        
        return True
        
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
        sql = "INSERT INTO Setup (Date, Description, File) VALUES (?, ?, ?)"
        self.cur.execute(sql,(self.now(),setup['description'],setup['file']))
        self.con.commit()
        return self.cur.lastrowid
    
    def new_entry(self, entry):
        """ Creates a new entry in the logbook. 
            Returns the ID of the newly created entry. 
        """
        sql = "INSERT INTO Logbook (DATE, User, Entry, File, Detectors, Variables, Setup, Comments) \
            values (?,?,?,?,?,?,?,?)"
        self.cur.execute(sql,(self.now(),entry['user'],entry['entry'],entry['file'],entry['detectors'],
                              entry['variables'],entry['setup'],entry['comments']))
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
        sql = 'SELECT Id, Description'
        self.cur.execute(sql)
        return self.cur.fetchall()
    
    def now(self):
        """ Returns the date formatted in a particular way to have entries
            consistent with each other. 
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def __del__(self):
        self.con.close()

if __name__ == "__main__":
    db = db_comm()
    db.cur.execute('SELECT SQLITE_VERSION()')
    data = db.cur.fetchone()
    print("SQLite3 version %s" % (data))
            
