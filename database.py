import os
import sys
import sqlite3
import hashlib
import hmac

#*******ADAPTED CODE*******************
# https://cx-freeze.readthedocs.io/en/6.11.0/faq.html?highlight=find
# https://www.geeksforgeeks.org/python/python-os-path-join-method/
# adapted the os.path.dirname() example 2 by pointing it towards the sys.executable directory
# adapted the cx-freeze "using data files" tutorial by removing the 2nd if function and changing the pointed directory
# used to find the database file while the application is running and bundled in pyinstaller by checking if the application is frozen
# if it's frozen, retrieve the root directory's file path and the path of the executable
# then connect the root directory path to the database name, before saving it in a variable

def getBasePath():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

dbName = os.path.join(getBasePath(), "scouts database.db")

#****ADAPTED CODE END*************************

def connectDb():
    db = sqlite3.connect(dbName)
    db.execute("PRAGMA foreign_keys = ON")
    return db

# builds the tables when the program is started, or when called, defining the data type and role of the field (e.g. foreign key, primary key)
# added cascade rules to ensure connected data is erased from all tables when the parent record is deleted
def buildTables():
    db = connectDb()
    table = db.cursor()

    table.execute("""
    CREATE TABLE IF NOT EXISTS Patrols (
        PatrolID INTEGER PRIMARY KEY AUTOINCREMENT,
        PatrolName TEXT NOT NULL,
        LeaderScoutID INTEGER,
        FOREIGN KEY (LeaderScoutID) REFERENCES Scouts(ScoutID)
    )
    """)

    table.execute("""
    CREATE TABLE IF NOT EXISTS Scouts (
         ScoutID INTEGER PRIMARY KEY AUTOINCREMENT,
         FirstName TEXT NOT NULL,
         LastName TEXT NOT NULL,
         DateOfBirth TEXT NOT NULL,
         ParentContact TEXT,
         MedicalInfo TEXT,
         PatrolID INTEGER,
         FOREIGN KEY (PatrolID) REFERENCES Patrols(PatrolID)
    )
    """)

    table.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT NOT NULL UNIQUE,
        PasswordHash TEXT NOT NULL,
        Role TEXT NOT NULL
    )
    """)

    table.execute("""
    CREATE TABLE IF NOT EXISTS Events (
        EventID INTEGER PRIMARY KEY AUTOINCREMENT,
        EventName TEXT NOT NULL,
        EventDate TEXT NOT NULL,
        Location TEXT,
        EventType TEXT NOT NULL,
        Description TEXT,
        Nights INTEGER NOT NULL,
        UserID INTEGER NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
    )
    """)

    table.execute("""
    CREATE TABLE IF NOT EXISTS Attendance (
        AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
        ScoutID INTEGER NOT NULL,
        EventID INTEGER NOT NULL,
        Status TEXT NOT NULL,
        FOREIGN KEY (ScoutID) REFERENCES Scouts(ScoutID) ON DELETE CASCADE,
        FOREIGN KEY (EventID) REFERENCES Events(EventID) ON DELETE CASCADE
    )
    """)

    table.execute("""
    CREATE TABLE IF NOT EXISTS Badges (
        BadgeID INTEGER PRIMARY KEY AUTOINCREMENT,
        BadgeName TEXT NOT NULL,
        Description TEXT NOT NULL,
        BadgeType TEXT NOT NULL
    )
    """)

    table.execute("""
    CREATE TABLE IF NOT EXISTS BadgeProgress (
        ProgressID INTEGER PRIMARY KEY AUTOINCREMENT,
        ScoutID INTEGER NOT NULL,
        BadgeID INTEGER NOT NULL,
        DateAwarded TEXT,
        AwardMethod TEXT NOT NULL,
        FOREIGN KEY (ScoutID) REFERENCES Scouts(ScoutID) ON DELETE CASCADE,
        FOREIGN KEY (BadgeID) REFERENCES Badges(BadgeID) 
    )
    """)

    table.execute("""
    CREATE TABLE IF NOT EXISTS BadgeRequirements (
        RequirementID INTEGER PRIMARY KEY AUTOINCREMENT,
        BadgeID INTEGER NOT NULL,
        RequiredAttendance INTEGER NOT NULL,
        EventType TEXT NOT NULL,
        OtherCriteria TEXT,
        FOREIGN KEY (BadgeID) REFERENCES Badges(BadgeID) ON DELETE CASCADE
    )
    """)

    table.execute("""
    CREATE TABLE IF NOT EXISTS Notes (
        NoteID INTEGER PRIMARY KEY AUTOINCREMENT,
        ScoutID INTEGER NOT NULL,
        UserID INTEGER NOT NULL,
        NoteText TEXT NOT NULL,
        DateCreated TEXT NOT NULL,
        FOREIGN KEY (ScoutID) REFERENCES Scouts(ScoutID) ON DELETE CASCADE,
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    )
    """)

    # builds indexes for frequently accessed data, such as last names or attendance details to improve efficiency 
    table.execute("CREATE INDEX IF NOT EXISTS idx_scout_lastname ON Scouts(LastName)")
    table.execute("CREATE INDEX IF NOT EXISTS idx_scout_patrol ON Scouts(PatrolID)")
    
    table.execute("CREATE INDEX IF NOT EXISTS idx_attendance_scout ON Attendance(ScoutID)")
    table.execute("CREATE INDEX IF NOT EXISTS idx_attendance_event ON Attendance(EventID)")
    
    table.execute("CREATE INDEX IF NOT EXISTS idx_badgeprogress_scout ON BadgeProgress(ScoutID)")
    table.execute("CREATE INDEX IF NOT EXISTS idx_badgeprogress_badge ON BadgeProgress(BadgeID)")

    db.commit()
    db.close()

#-----------------------------------------------------------------------------------------------------------------
# functions for scout data GUI

# inserts the user inputs into the scouts table
def addScout(firstName, lastName, dob, parentContact, medicalInfo, patrolID=None):
    db = connectDb()
    table = db.cursor()
    table.execute("""
       INSERT INTO Scouts(FirstName, LastName, DateOfBirth, ParentContact, MedicalInfo, PatrolID)
       VALUES (?, ?, ?, ?, ?, ?)
       """, (firstName, lastName, dob, parentContact, medicalInfo, patrolID))
    db.commit()
    db.close()

#******ADAPTED CODE****************
# https://imarranz.github.io/essential-guide-to-sqlite/08_joins/086_examples.html 
# adapted "Left Join" example by changing the field names, table name and added an ORDER BY function
# used to store and display the associated patrol name instead of a patrol ID, aiding readibility

# fetches all the scout data in the table, and outputs it
def allScouts():
    db = connectDb()
    table = db.cursor()
    table.execute("""
        SELECT Scouts.ScoutID,
               Scouts.FirstName,
               Scouts.LastName,
               Scouts.DateOfBirth,
               Scouts.ParentContact,
               Scouts.MedicalInfo,
               Patrols.PatrolName
        FROM Scouts
        LEFT JOIN Patrols ON Scouts.PatrolID = Patrols.PatrolID
        ORDER BY Scouts.LastName, Scouts.FirstName
    """)
    data = table.fetchall()
    db.close()
    return data

# searches for scout records where the first name or last name contains the input text
def searchScout(searchInput):
    db = connectDb()
    table = db.cursor()
    table.execute("""
        SELECT Scouts.ScoutID,
               Scouts.FirstName,
               Scouts.LastName,
               Scouts.DateOfBirth,
               Scouts.ParentContact,
               Scouts.MedicalInfo,
               Patrols.PatrolName
        FROM Scouts
        LEFT JOIN Patrols ON Scouts.PatrolID = Patrols.PatrolID
        WHERE Scouts.FirstName LIKE ? OR Scouts.LastName LIKE ?
        ORDER BY Scouts.LastName, Scouts.FirstName
    """, (f"%{searchInput}%", f"%{searchInput}%"))
    data = table.fetchall()
    db.close()
    return data

#*********ADAPTED CODE END****************

# deletes a scout with the selected scoutID from the table
def deleteScout(scoutID):
    db = connectDb()
    table = db.cursor()
    table.execute("DELETE FROM Scouts WHERE ScoutID = ?", (scoutID,))
    db.commit()
    db.close()



# overwrites the data in the selected record of the defined scoutID with the user inputs
def updateScout(scoutID, firstName, lastName, dob, parentContact, medicalInfo):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      UPDATE Scouts
      SET FirstName = ?, LastName = ?, DateOfBirth = ?, ParentContact = ?, MedicalInfo = ?
      WHERE ScoutID = ?
      """, (firstName, lastName, dob, parentContact, medicalInfo, scoutID))
    db.commit()
    db.close()

#---------------------------------------------------------------------------------------------
# functions for event GUI

# fetches all event data, orders them by event date, then returns them
def allEvents():
    db = connectDb()
    table = db.cursor()
    table.execute("""
       SELECT EventID, EventName, EventDate, Location, EventType, Nights, UserID
       FROM Events
       ORDER BY EventDate
       """)
    records = table.fetchall()
    db.close()
    return records

# adds the user's inputs into the database 
def addEvent(eventName, eventDate, location, eventType, description, nights, userID):
    db = connectDb()
    table = db.cursor()
    table.execute("""
    INSERT INTO Events(EventName, EventDate, Location, EventType, Description, Nights, UserID)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (eventName, eventDate, location, eventType, description, nights, userID))
    db.commit()
    db.close()

# removes the selected event record from the table
def deleteEvent(eventID):
    db = connectDb()
    table = db.cursor()
    table.execute("DELETE FROM Events WHERE EventID = ?", (eventID,))
    db.commit()
    db.close()

# modifies the event variables in the selected record based on the user's inputs
def updateEvent(eventID, eventName, eventDate, location, eventType, description, nights, userID):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      UPDATE Events
      SET EventName = ?, EventDate = ?, Location = ?, EventType = ?, Description = ?, Nights = ?, UserID = ?
      WHERE EventID = ?
      """, (eventName, eventDate, location, eventType, description, nights, userID, eventID))
    db.commit()
    db.close()
    
# compares the name and event date of every record with the user's inputs, then returns any similar records
def searchEvent(searchInput):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT EventID, EventName, EventDate, Location, EventType, Nights, UserID
      FROM Events
      WHERE EventName LIKE ? OR EventType LIKE ?
      ORDER BY EventDate
      """, (f"%{searchInput}%", f"%{searchInput}%"))
    data = table.fetchall()
    db.close()
    return data

# selects an event by it's eventID, then outputs it
def getEventByID(eventID):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT EventID, EventName, EventDate, Location, EventType, Description, Nights, UserID
      FROM Events
      WHERE EventID = ?
    """, (eventID,))
    data = table.fetchone()
    db.close()
    return data

#----------------------------------------------------------------------------------------------
# attendance GUI functions


#**************************ADAPTED CODE***********************************************
# https://imarranz.github.io/essential-guide-to-sqlite/08_joins/086_examples.html 
# used the 'Joining Multiple Tables' and 'Inner Join' example to display useful info instead of foreign keys
# adapted by changing the table names, field names and adding an 'ORDER BY' command 

# selects and outputs all the records and their associated data from the attendance table
def allAttendance():
    db = connectDb()
    table = db.cursor()
    table.execute("""
       SELECT Attendance.AttendanceID,
              Scouts.FirstName,
              Scouts.LastName,
              Events.EventName,
              Events.EventDate,
              Attendance.Status
        FROM Attendance
        INNER JOIN Scouts ON Attendance.ScoutID = Scouts.ScoutID
        INNER JOIN Events ON Attendance.EventID = Events.EventID
        ORDER BY Events.EventDate
    """)
    data = table.fetchall()
    db.close()
    return data

# searches the attendance table for a specified record, then outputs it if found
def searchAttendance(searchInput):
    db = connectDb()
    table = db.cursor()
    table.execute("""
       SELECT Attendance.AttendanceID,
              Scouts.FirstName,
              Scouts.LastName,
              Events.EventName,
              Events.EventDate,
              Attendance.Status
        FROM Attendance
        INNER JOIN Events ON Attendance.EventID = Events.EventID
        INNER JOIN Scouts ON Attendance.ScoutID = Scouts.ScoutID
        WHERE Scouts.FirstName LIKE ?
           OR Scouts.LastName LIKE ?
           OR Events.EventName LIKE ?
           OR Attendance.Status LIKE ?
        ORDER BY Events.EventDate
    """, (f"%{searchInput}%", f"%{searchInput}%", f"%{searchInput}%", f"%{searchInput}%"))
    data = table.fetchall()
    db.close()
    return data

#***************************END OF ADAPTED CODE*************************************

# adds a record to the attendance table
def addAttendance(scoutID, eventID, status):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      INSERT INTO Attendance (ScoutID, EventID, Status)
      VALUES (?, ?, ?)
    """, (scoutID, eventID, status))
    db.commit()
    db.close()

# removes a specified record from the attendance table
def deleteAttendance(attendanceID):
    db = connectDb()
    table = db.cursor()
    table.execute("DELETE FROM Attendance WHERE AttendanceID = ?", (attendanceID,))
    db.commit()
    db.close()

# outputs all the available scout records so they can be listed in a dropdown field
def scoutList():
    db = connectDb()
    table = db.cursor()
    table.execute("""
       SELECT ScoutID, FirstName, LastName
       FROM Scouts
       ORDER BY LastName, FirstName
       """)
    data = table.fetchall()
    db.close()
    return data

# outputs all the available event records so they can be listed in a dropdown field
def eventList():
    db = connectDb()
    table = db.cursor()
    table.execute("""
       SELECT EventID, EventName, EventDate
       FROM Events
       ORDER BY EventDate
       """)
    data = table.fetchall()
    db.close()
    return data

#---------------badge requirement GUI functions-------------------

#*****************ADAPTED CODE**************************
# https://imarranz.github.io/essential-guide-to-sqlite/08_joins/086_examples.html 
# used the 'Joining Multiple Tables' and 'Left Join' example to display and search for useful info instead of outputting foreign keys
# adapted by changing the table names, field names and adding an 'ORDER BY' command to output data in a understandable way
# assume that all 'LEFT JOIN' SQL queue

# stores and outputs all the badge requirement records
def allBadgeRequirements():
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT BadgeRequirements.RequirementID,
          Badges.BadgeName,
          BadgeRequirements.RequiredAttendance,
          BadgeRequirements.EventType,
          BadgeRequirements.OtherCriteria
      FROM BadgeRequirements
      LEFT JOIN Badges ON BadgeRequirements.BadgeID = Badges.BadgeID
      ORDER BY Badges.BadgeName
    """)
    data = table.fetchall()
    db.close()
    return data

# searches the table for a similar record, then outputs it if found
def searchBadgeRequirements(searchInput):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT BadgeRequirements.RequirementID,
          Badges.BadgeName,
          BadgeRequirements.RequiredAttendance,
          BadgeRequirements.EventType,
          BadgeRequirements.OtherCriteria
      FROM BadgeRequirements
      LEFT JOIN Badges ON BadgeRequirements.BadgeID = Badges.BadgeID
      WHERE Badges.BadgeName LIKE ?
        OR BadgeRequirements.EventType LIKE ?
        OR BadgeRequirements.OtherCriteria LIKE ?
      ORDER BY Badges.BadgeName
    """, (f"%{searchInput}", f"%{searchInput}%", f"%{searchInput}"))
    data = table.fetchall()
    db.close()
    return data

#***********************ADAPTED CODE END******************************

# adds a record with the specified values by the user
def addBadgeRequirement(badgeID, requiredAttendance, eventType, otherCriteria):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      INSERT INTO BadgeRequirements (BadgeID, RequiredAttendance, EventType, OtherCriteria)
      VALUES (?, ?, ?, ?)
    """, (badgeID, requiredAttendance, eventType, otherCriteria))
    db.commit()
    db.close()

# updates the specified record by the values inputted by the user
def updateBadgeRequirement(requirementID, badgeID, requiredAttendance, eventType, otherCriteria):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      UPDATE BadgeRequirements
      SET BadgeID = ?, RequiredAttendance = ?, EventType = ?, OtherCriteria = ?
      WHERE RequirementID = ?
    """, (badgeID, requiredAttendance, eventType, otherCriteria, requirementID))
    db.commit()
    db.close()

# deletes a specified record by the user
def deleteBadgeRequirement(requirementID):
    db = connectDb()
    table = db.cursor()
    table.execute("DELETE FROM BadgeRequirements WHERE RequirementID = ?", (requirementID,))
    db.commit()
    db.close()

# outputs the available badges so they can be displayed in a dropdown list
def badgeList():
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT BadgeID, BadgeName
      FROM Badges
      ORDER BY BadgeName
    """)
    data = table.fetchall()
    db.close()
    return data

# ---------------------------------------------------------------------
# badge automation logic functions

# gathers and outputs all the available scout IDs 
def allScoutIDs():
    db = connectDb()
    table = db.cursor()
    table.execute("SELECT ScoutID from Scouts")
    data = table.fetchall()
    db.close()
    return data

# gathers and outputs all the available badge requirement IDs
def allRequirementRules():
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT RequirementID, BadgeID, RequiredAttendance, EventType, OtherCriteria
      FROM BadgeRequirements
    """)
    data = table.fetchall()
    db.close()
    return data

#************ADAPTED CODE START*****************
# https://www.sqliz.com/posts/how-count-function-works-in-sqlite/
# https://www.sqlitetutorial.net/sqlite-join/
# used 'Left Join' from the 2nd link and the COUNT(*) tutorial from the 1st link
# adapted by changing the field names, table names and combining COUNT and JOIN BY 
# built to count the number of times a scout has been to a specific type of event by filtering the attendance records
# by specific event type, and whether the selected scout was present

# adds up the number of times a scout has been to a specific event, e.g. hike - doesn't take into account the number of nights
def scoutAttendanceByType(scoutID, eventType):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT COUNT(*)
      FROM Attendance
      LEFT JOIN Events ON Attendance.EventID = Events.EventID
      WHERE Attendance.ScoutID = ?
      AND Attendance.Status = "Present"
      AND Events.EventType = ?
    """, (scoutID, eventType))
    data = table.fetchone()[0]
    db.close()
    return data

# finds the total for the number of nights a scout has been to a specific event, like a camp
def scoutNightsByType(scoutID, eventType):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT COALESCE(SUM(Events.Nights), 0)
      FROM Attendance
      LEFT JOIN Events ON Attendance.EventID = Events.EventID
      WHERE Attendance.ScoutID = ?
      AND Attendance.Status = "Present"
      AND Events.EventType = ?
    """, (scoutID, eventType))
    data = table.fetchone()[0]
    db.close()
    return data

#******ADAPTED CODE END****************

# checks the badge progress records to see if a specific badge has already been awarded to the specified scout
def badgeAlreadyAwarded(scoutID, badgeID):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT ProgressID
      FROM BadgeProgress
      WHERE ScoutID = ? AND BadgeID = ?
    """, (scoutID, badgeID))
    data = table.fetchone()
    db.close()
    return data is not None

# awards the badge to the scouts by adding the specified data into the table
def awardBadge(scoutID, badgeID, dateAwarded, awardMethod):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      INSERT INTO BadgeProgress (ScoutID, BadgeID, DateAwarded, AwardMethod)
      VALUES (?, ?, ?, ?)
    """, (scoutID, badgeID, dateAwarded, awardMethod))
    db.commit()
    db.close()

#---------------badge progress GUI functions----------------------

# stores and outputs all the available badge progress records
def allBadgeProgress():
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT BadgeProgress.ProgressID,
             Scouts.FirstName,
             Scouts.LastName,
             Badges.BadgeName,
             BadgeProgress.DateAwarded,
             BadgeProgress.AwardMethod
       FROM BadgeProgress
       LEFT JOIN Scouts ON BadgeProgress.ScoutID = Scouts.ScoutID
       LEFT JOIN Badges ON Badgeprogress.BadgeID = Badges.BadgeID
       ORDER BY BadgeProgress.DateAwarded
    """)
    data = table.fetchall()
    db.close()
    return data

# searches the badge progress table for a specific record specified by the search input variable
def searchBadgeProgress(searchInput):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT BadgeProgress.ProgressID,
         Scouts.FirstName,
         Scouts.LastName,
         Badges.BadgeName,
         BadgeProgress.DateAwarded,
         BadgeProgress.AwardMethod
      FROM BadgeProgress
      LEFT JOIN Scouts ON BadgeProgress.ScoutID = Scouts.ScoutID
      LEFT JOIN Badges ON Badgeprogress.BadgeID = Badges.BadgeID
      WHERE Scouts.FirstName LIKE ?
         OR Scouts.LastName LIKE ?
         OR Badges.BadgeName LIKE ?
         OR BadgeProgress.AwardMethod LIKE ?
      ORDER BY BadgeProgress.DateAwarded
    """, (f"%{searchInput}%", f"%{searchInput}%", f"%{searchInput}%", f"%{searchInput}%"))
    data = table.fetchall()
    db.close()
    return data

# deletes a specified badge progress record
def deleteBadgeProgress(progressID):
    db = connectDb()
    table = db.cursor()
    table.execute("DELETE FROM BadgeProgress WHERE ProgressID = ?", (progressID,))
    db.commit()
    db.close()

#-------------------------------------
# user login functions

# hashes the inputted password 
def hashPassword(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200_000)
    return salt.hex() + ':' + key.hex()

# verifies the inputted password matches the stored hash
def verifyPassword(password, storedHash):
    salt, oldKey = storedHash.split(":")
    newKey = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 200_000)
    return hmac.compare_digest(oldKey, newKey.hex())
    

# adds the specified data into the user table, making a new record
def addUser(username, password, role):
    db = connectDb()
    table = db.cursor()
    
    passwordHash = hashPassword(password)

    table.execute("""
      INSERT INTO Users(Username, PasswordHash, Role)
      VALUES (?, ?, ?)  
    """, (username, passwordHash, role))
    db.commit()
    db.close()

# searches the user table and outputs any records with a similar name
def getUserByUsername(username):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT UserID, Username, PasswordHash, Role
      FROM Users
      WHERE Username = ?
    """, (username,))
    data = table.fetchone()
    db.close()
    return data

# checks the user's inputted details, and if they match with any records
def checkLogin(username, password):
    user = getUserByUsername(username)

    if user is None:
        return None

    userID, storedUsername, storedHash, role = user

    if verifyPassword(password, storedHash):
        return user

    return None

#----------------------------------
# database functions for dashboard

#*****************ADAPTED CODE*******************************
# https://www.sqliz.com/posts/how-count-function-works-in-sqlite/
# http://2015.padjo.org/tutorials/sql-basics/limit-and-order/
#  adapted by changing the field names and table names
# used the "ORDER BY and LIMIT" example at the bottom of link #2 for RecentBadgeAwards
# built to gather the lastest 5 badge awards and their associated records, then store them in the data variable
# used the "Counting Everything vs. Counting Specifics" example at the top of link #1 for every other function
# counts the number of records in the specified table, then outputs the value

def totalScouts():
    db = connectDb()
    table = db.cursor()
    table.execute("SELECT COUNT(*) FROM Scouts")
    data = table.fetchone()[0]
    db.close()
    return data

def totalEvents():
    db = connectDb()
    table = db.cursor()
    table.execute("SELECT COUNT(*) FROM Events")
    data = table.fetchone()[0]
    db.close()
    return data

def totalAttendanceRecords():
    db = connectDb()
    table = db.cursor()
    table.execute("SELECT COUNT(*) FROM Attendance")
    data = table.fetchone()[0]
    db.close()
    return data

def totalBadgesAwarded():
    db = connectDb()
    table = db.cursor()
    table.execute("SELECT COUNT(*) FROM BadgeProgress")
    data = table.fetchone()[0]
    db.close()
    return data

def recentBadgeAwards():
    db = connectDb()
    table = db.cursor()
    table.execute("""
        SELECT s.FirstName,
               s.LastName,
               b.BadgeName,
               bp.DateAwarded,
               bp.AwardMethod
        FROM BadgeProgress AS bp
        JOIN Scouts AS s ON bp.ScoutID = s.ScoutID
        JOIN Badges AS b ON bp.BadgeID = b.BadgeID
        ORDER BY bp.ProgressID DESC
        LIMIT 5
    """)
    data = table.fetchall()
    db.close()
    return data

#--------------------functions for bulk patrol assignment----------------

def bulkUpdateScoutPatrol(scoutIDs, patrolID):
    db = connectDb()
    table = db.cursor()

    for scoutID in scoutIDs:
        table.execute("""
          UPDATE Scouts
          SET PatrolID = ?
          WHERE ScoutID = ?
        """, (patrolID, scoutID))
    db.commit()
    db.close()

# outputs all of the patrol records, including the patrol name and it's ID for the dropdown table
def patrolList():
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT PatrolID, PatrolName
      FROM Patrols
      ORDER BY PatrolName
    """)
    data = table.fetchall()
    db.close()
    return data

#----------------functions for patrol GUI----------------------

def allPatrols():
    db = connectDb()
    table = db.cursor()
    table.execute("""
        SELECT PatrolID, PatrolName, LeaderScoutID
        FROM Patrols
        ORDER BY PatrolName
    """)
    data = table.fetchall()
    db.close()
    return data

def addPatrol(patrolName, leaderScoutID=None):
    db = connectDb()
    table = db.cursor()
    table.execute("""
       INSERT INTO Patrols (PatrolName, LeaderScoutID)
       VALUES (?, ?)
    """, (patrolName, leaderScoutID))
    db.commit()
    db.close()

def deletePatrol(patrolID):
    db = connectDb()
    table = db.cursor()
    table.execute("DELETE FROM Patrols WHERE PatrolID = ?", (patrolID,))
    db.commit()
    db.close()

def updatePatrol(patrolID, patrolName, leaderScoutID=None):
    db = connectDb()
    table = db.cursor()
    table.execute("""
       UPDATE Patrols
       SET PatrolName = ?, LeaderScoutID = ?
       WHERE PatrolID = ?
    """, (patrolName, leaderScoutID, patrolID))
    db.commit()
    db.close()

def searchPatrol(searchInput):
    db = connectDb()
    table = db.cursor()
    table.execute("""
      SELECT PatrolID, PatrolName, LeaderScoutID
      FROM Patrols
      WHERE PatrolName LIKE ?
      ORDER BY PatrolName
    """, (f"%{searchInput}%",))
    data = table.fetchall()
    db.close()
    return data

#---------------------------------------------------
# functions for user management GUI

def allUsers():
    db = connectDb()
    table = db.cursor()
    table.execute("""
        SELECT UserID, Username, Role
        FROM Users
        ORDER BY Username
    """)
    data = table.fetchall()
    db.close()
    return data


def searchUsers(searchInput):
    db = connectDb()
    table = db.cursor()
    table.execute("""
        SELECT UserID, Username, Role
        FROM Users
        WHERE Username LIKE ? OR Role LIKE ?
        ORDER BY Username
    """, (f"%{searchInput}%", f"%{searchInput}%"))
    data = table.fetchall()
    db.close()
    return data


def updateUser(userID, username, role):
    db = connectDb()
    table = db.cursor()
    table.execute("""
        UPDATE Users
        SET Username = ?, Role = ?
        WHERE UserID = ?
    """, (username, role, userID))
    db.commit()
    db.close()


def deleteUser(userID):
    db = connectDb()
    table = db.cursor()
    table.execute("DELETE FROM Users WHERE UserID = ?", (userID,))
    db.commit()
    db.close()

# changes the user's password if they forget it
def updateUserPassword(userID, newPassword):
    db = connectDb()
    table = db.cursor()
    newHash = hashPassword(newPassword)
    table.execute("""
        UPDATE Users
        SET PasswordHash = ?
        WHERE UserID = ?
    """, (newHash, userID))
    db.commit()
    db.close()

#-------------------------------------
# functions for table filtering

def filterScoutsByPatrol(patrolName):
    db = connectDb()
    table = db.cursor()
    table.execute("""
        SELECT Scouts.ScoutID,
               Scouts.FirstName,
               Scouts.LastName,
               Scouts.DateOfBirth,
               Scouts.ParentContact,
               Scouts.MedicalInfo,
               Patrols.PatrolName
        FROM Scouts
        LEFT JOIN Patrols ON Scouts.PatrolID = Patrols.PatrolID
        WHERE Patrols.PatrolName = ?
        ORDER BY Scouts.LastName, Scouts.FirstName
    """, (patrolName,))
    data = table.fetchall()
    db.close()
    return data

#------------------------------------
# function for the action queue

def latestScout():
    db = connectDb()
    table = db.cursor()
    table.execute("""
        SELECT ScoutID, FirstName, LastName
        FROM Scouts
        ORDER BY ScoutID DESC
        LIMIT 1
    """)
    data = table.fetchone()
    db.close()
    return data

#------------------------------------
# test functions

def addTestUser():
    db = connectDb()
    table = db.cursor()
    table.execute("SELECT UserID FROM Users WHERE Username = 'admin'")
    if table.fetchone() is None:
        table.execute("""
          INSERT INTO Users(Username, PasswordHash, Role)
          VALUES (?, ?, ?)
        """, ('admin', hashPassword('admin123'), 'Admin'))
        db.commit()
    db.close()

def seedReferenceData():
    db = connectDb()
    table = db.cursor()

    table.execute("SELECT COUNT(*) FROM Patrols")
    if table.fetchone()[0] == 0:
        for name in ("Cobras", "Falcons", "Panthers", "Otters"):
            table.execute("INSERT INTO Patrols (PatrolName, LeaderScoutID) VALUES (?, ?)", (name, None))

    table.execute("SELECT COUNT(*) FROM Badges")
    if table.fetchone()[0] == 0:
        badges = [
            ("Hiker", "Awarded for attending hikes", "Activity"),
            ("Camper", "Awarded for nights spent camping", "Activity"),
            ("Community Helper", "Awarded for community events", "Service"),
        ]
        for badge in badges:
            table.execute("INSERT INTO Badges (BadgeName, Description, BadgeType) VALUES (?, ?, ?)", badge)

    db.commit()
    db.close()