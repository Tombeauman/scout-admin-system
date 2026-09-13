# Scout Administration Dashboard
Scout troop management system built using SQLite and tkinter on Python 3.9.
Coursework submission for the 2026 AQA A-Level Computer Science NEA, being awarded 69/75 marks.

To run, clone and run python main.py.
 Note that database and test data are created automatically on first run.

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
- Layered structure - each feature has it's own GUI module, so no SQL in the interface
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

