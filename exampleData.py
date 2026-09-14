from database import connectDb, buildTables, addTestUser

PATROLS = ["Cobras", "Falcons", "Panthers", "Otters"]

BADGES = [
    ("Hiker",            "Awarded for attending hikes",              "Activity"),
    ("Camper",           "Awarded for nights spent camping",         "Activity"),
    ("Community Helper", "Awarded for attending community events",   "Service"),
    ("Navigator",        "Awarded for map and compass work",         "Skill"),
]

# firstName, lastName, dob, parentContact, medicalInfo, patrolIndex
SCOUTS = [
    ("Alex",   "Turner",   "07/03/2011", "07700 900123", "Asthma - inhaler in kit bag", 0),
    ("Priya",  "Shah",     "23/11/2014", "07700 900456", "",                            1),
    ("Thomas", "Bennett",  "17/06/2012", "07700 900789", "Dyslexia",                    2),
    ("Grace",  "Okafor",   "02/09/2013", "07700 900234", "Nut allergy - EpiPen carried", 0),
    ("Daniel", "Whitmore", "14/01/2012", "07700 900567", "",                            1),
    ("Isla",   "Ferguson", "30/05/2014", "07700 900890", "Wears glasses",               2),
    ("Samuel", "Adeyemi",  "11/08/2011", "07700 900345", "",                            3),
    ("Chloe",  "Marsden",  "26/02/2013", "07700 900678", "Hay fever",                   3),
]

# eventName, eventDate, location, eventType, description, nights
EVENTS = [
    ("Autumn Hike",        "12/10/2025", "Windsor Great Park", "Hike",      "Six mile circular walk with map work.",        0),
    ("District Camp",      "07/11/2025", "Longridge",          "Camp",      "Weekend camp with three other troops.",        2),
    ("Winter Night Hike",  "06/12/2025", "Chobham Common",     "Hike",      "Evening navigation exercise with head torches.", 0),
    ("Food Bank Sort",     "18/01/2026", "Slough",             "Community", "Sorting and packing donations.",               0),
    ("Spring Camp",        "21/03/2026", "Gilwell Park",       "Camp",      "Three nights under canvas, pioneering focus.",  3),
    ("River Clean-Up",     "25/04/2026", "Datchet",            "Community", "Litter pick along the riverbank.",             0),
    ("Summer Hike",        "16/05/2026", "Burnham Beeches",    "Hike",      "Eight mile hike with contour work.",           0),
]

# badgeName, requiredAttendance, eventType, otherCriteria
REQUIREMENTS = [
    ("Hiker",            3, "Hike",      ""),
    ("Camper",           4, "Camp",      "Nights"),
    ("Community Helper", 2, "Community", ""),
    ("Navigator",        2, "Hike",      ""),
]

# scouts who miss a session, keyed by (scoutIndex, eventIndex)
ABSENCES = {(1, 2), (4, 0), (6, 4), (2, 5), (7, 1)}


def clearDemoTables():
    db = connectDb()
    table = db.cursor()
    for name in ("BadgeProgress", "BadgeRequirements", "Attendance",
                 "Notes", "Events", "Scouts", "Badges", "Patrols"):
        table.execute(f"DELETE FROM {name}")
# reset the autoincrement counters so IDs start at 1 again
    table.execute("DELETE FROM sqlite_sequence")
    db.commit()
    db.close()


def seed():
    db = connectDb()
    table = db.cursor()

# patrols
    patrolIDs = []
    for name in PATROLS:
        table.execute("INSERT INTO Patrols (PatrolName, LeaderScoutID) VALUES (?, ?)", (name, None))
        patrolIDs.append(table.lastrowid)

# badges
    badgeIDs = {}
    for name, description, badgeType in BADGES:
        table.execute("INSERT INTO Badges (BadgeName, Description, BadgeType) VALUES (?, ?, ?)",
                      (name, description, badgeType))
        badgeIDs[name] = table.lastrowid

# scouts
    scoutIDs = []
    for firstName, lastName, dob, contact, medical, patrolIndex in SCOUTS:
        table.execute("""
            INSERT INTO Scouts (FirstName, LastName, DateOfBirth, ParentContact, MedicalInfo, PatrolID)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (firstName, lastName, dob, contact, medical, patrolIDs[patrolIndex]))
        scoutIDs.append(table.lastrowid)

# the admin user created events, so find their UserID
    table.execute("SELECT UserID FROM Users WHERE Username = 'admin'")
    row = table.fetchone()
    adminID = row[0] if row else 1

# events
    eventIDs = []
    for eventName, eventDate, location, eventType, description, nights in EVENTS:
        table.execute("""
            INSERT INTO Events (EventName, EventDate, Location, EventType, Description, Nights, UserID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (eventName, eventDate, location, eventType, description, nights, adminID))
        eventIDs.append(table.lastrowid)

# attendance - everyone present unless listed in ABSENCES
    for scoutIndex, scoutID in enumerate(scoutIDs):
        for eventIndex, eventID in enumerate(eventIDs):
            status = "Absent" if (scoutIndex, eventIndex) in ABSENCES else "Present"
            table.execute("INSERT INTO Attendance (ScoutID, EventID, Status) VALUES (?, ?, ?)",
                          (scoutID, eventID, status))

# badge requirements
    for badgeName, requiredAttendance, eventType, otherCriteria in REQUIREMENTS:
        table.execute("""
            INSERT INTO BadgeRequirements (BadgeID, RequiredAttendance, EventType, OtherCriteria)
            VALUES (?, ?, ?, ?)
        """, (badgeIDs[badgeName], requiredAttendance, eventType, otherCriteria))

# one badge awarded by hand, so the Award Method column shows both routes
    table.execute("""
        INSERT INTO BadgeProgress (ScoutID, BadgeID, DateAwarded, AwardMethod)
        VALUES (?, ?, ?, ?)
    """, (scoutIDs[0], badgeIDs["Navigator"], "20/05/2026", "Manual"))

    db.commit()
    db.close()


if __name__ == "__main__":
    buildTables()
    addTestUser()
    clearDemoTables()
    addTestUser()      
    seed()
    print(f"Seeded {len(PATROLS)} patrols, {len(BADGES)} badges, "
          f"{len(SCOUTS)} scouts, {len(EVENTS)} events, "
          f"{len(SCOUTS) * len(EVENTS)} attendance records and "
          f"{len(REQUIREMENTS)} badge requirements.")
    print("Log in as admin / admin123, then press 'Run Badge Automation' on the Badge Progress tab.")
