# Scout Administration Dashboard
Scout troop management system built using SQLite and tkinter on Python 3.9.
Coursework submission for the 2026 AQA A-Level Computer Science NEA, awarded 69/75 marks.

Built using experience as a Scouts volunteer leader, replacing the original spreadsheet format initially used by the group.

To run, clone and run python main.py.
Note that database and test data are created automatically on first run.
To generate test data, run exampleData.py independently before main.py.

# Project Overview

This software is designed to help scout leaders through:
- Role-based access control - two roles, admin and leader
- Scout records - add, update, delete and search members
- Patrol management - create and manage patrols
- Event tracking - record events with type, location, date and description
- Attendance - mark scouts present or absent per event
- Badge requirements - define criteria per badge as an attendance threshold for a specific event type
- Automated badge awarding - evaluate every member against every rule, and award if met
- Dashboard - summary count for scouts, events, and a list of recent awards
- Recent actions queue - a dashboard showing the five last record changes

Design Notes
- Layered structure - each feature has its own GUI module, so no SQL in the interface
- Parameterised queries - prevents user input from being concatenated into SQL
- Enforced referential integrity - forced foreign keys for cascade deletes, ensuring no orphaned records
- Indexed lookups - ensures lookup speed as dataset gets bigger
- Access control filters data - leader users are locked out of both viewing sensitive data and destructive functions
- database JOINs - ensure readable outputs instead of foreign keys
- Password storage - Passwords are hashed with PBKDF2-HMAC-SHA256 using a per-user random salt and 200,000 iterations

Things I'd change:
- Dates are stored as DD/MM/YYYY text, so they sort alphabetically rather than chronologically. ISO format would fix it.
- Date validation only checks the format, so it accepts 31/02/2026.
- Role checks are in the interface rather than the database functions, so they're bypassable by anything calling those functions directly.
- Error handling - foreign key failures can crash rather than showing a message.

# GUI Example Images

**Dashboard**
<img width="988" height="820" alt="Screenshot 2026-09-14 154132" src="https://github.com/user-attachments/assets/3702a472-c950-4c1b-9d94-c286c2dce205" />

**Admin view - full access to all fields**
<img width="992" height="821" alt="Screenshot 2026-09-14 154107" src="https://github.com/user-attachments/assets/57dc2082-c8ae-4450-a059-f35f190f034f" />

**Leader view - sensitive fields and destructive actions removed**
<img width="989" height="819" alt="Screenshot 2026-09-14 154227" src="https://github.com/user-attachments/assets/f7a69fcc-c09d-4284-8e8e-6a1a476f42d0" />

**Badge Progress - note both automated and manually awarded badges**
<img width="993" height="820" alt="Screenshot 2026-09-14 154151" src="https://github.com/user-attachments/assets/455261fc-34d8-4499-ae5f-716555c5445c" />
