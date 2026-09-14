import tkinter as tk
from tkinter import messagebox, ttk
from database import addAttendance, allAttendance, deleteAttendance, searchAttendance, scoutList, eventList
from lib import getScoutIDFromSelection

def createAttendancePage(parent, loggedInUser):
    global tree, scoutDropDown, eventDropDown, statusDropDown, searchEntry

    currentUserRole = loggedInUser[3]

#---------------------functions for GUI---------------------------

    # loads the attendance records from the table, outputs them in the interface
    def loadAttendance():
        for row in tree.get_children():
            tree.delete(row)

        for record in allAttendance():
            tree.insert("", tk.END, values=record)

    # clears the user's scout and status input so attendance status for one event can be added faster
    def clearInputs():
        scoutDropDown.set("")
        statusDropDown.set("")

    # clears all of the inputs, including the selected event
    def clearAllInputs():
        scoutDropDown.set("")
        eventDropDown.set("")
        statusDropDown.set("")

    # gathers and stores all the event IDs so they can be displayed in the dropdown
    def getEventIDFromSelection(selection):
        return int(selection.split(" - ")[0])

    # validates the user's inputs so the required info for badge automation exists, reducing crashes / badge awarding inaccuracies
    def validateAttendanceInput(scoutSelection, eventSelection, statusSelection):
        if scoutSelection == "" or eventSelection == "" or statusSelection == "":
            messagebox.showerror("Input Error", "Scout, event and status must all be selected.")
            return False
        return True

    # validates and adds the user's inputs into the table
    def addAttendanceToDB():
        scoutSelection = scoutDropDown.get()
        eventSelection = eventDropDown.get()
        statusSelection = statusDropDown.get()

        if not validateAttendanceInput(scoutSelection, eventSelection, statusSelection):
            return

        scoutID = getScoutIDFromSelection(scoutSelection)
        eventID = getEventIDFromSelection(eventSelection)

        addAttendance(scoutID, eventID, statusSelection)

        loadAttendance()
        clearInputs()
        messagebox.showinfo("Success", "Attendance record added successfully.")

    # deletes a selected record from the table - if none are selected, an error message is displayed
    def deleteSelectedAttendance():
        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select an attendance record to delete.")
            return

        chosenRecord = tree.item(chosen[0])
        recordValues = chosenRecord["values"]
        attendanceID = recordValues[0]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Attendance ID {attendanceID}?")

        if confirm:
            deleteAttendance(attendanceID)
            loadAttendance()
            messagebox.showinfo("Success", "Attendance record deleted successfully.")

    # searches the attendance records for a specific record, as defined by the user's search input
    def searchAttendanceRecords():
        searchInput = searchEntry.get()

        for row in tree.get_children():
            tree.delete(row)

        results = searchAttendance(searchInput)

        for record in results:
            tree.insert("", tk.END, values=record)

    # resets the search input field and refreshes the attendance table
    def resetSearch():
        searchEntry.delete(0, tk.END)
        loadAttendance()

    # loads the avaiable scouts and their first name, last name and ID, so they can be displayed in a dropdown table
    def loadScoutOptions():
        scouts = scoutList()
        scoutOptions = [f"{scout[0]} - {scout[2]}, {scout[1]}" for scout in scouts]
        scoutDropDown["values"] = scoutOptions

    # loads the avaiable events, so they can be displayed in a dropdown table
    def loadEventOptions():
        events = eventList()
        eventOptions = [f"{event[0]} - {event[1]} ({event[2]})" for event in events]
        eventDropDown["values"] = eventOptions

    # refreshes the table and the dropdown tables
    def refreshAttendance():
        loadScoutOptions()
        loadEventOptions()
        loadAttendance()


#------page layout--------------------
    titleLabel = tk.Label(parent, text="Attendance Records", font=("Arial", 16))
    titleLabel.pack(pady=10)

    roleLabel = tk.Label(parent, text=f"Logged in as: {loggedInUser[1]} ({currentUserRole})", font=("Arial", 10))
    roleLabel.pack(pady=2)

    inputFrame = tk.Frame(parent)
    inputFrame.pack(pady=10)

    tk.Label(inputFrame, text="Scout").grid(row=0, column=0, padx=5, pady=2)
    tk.Label(inputFrame, text="Event").grid(row=0, column=1, padx=5, pady=2)
    tk.Label(inputFrame, text="Status").grid(row=0, column=2, padx=5, pady=2)

    scoutDropDown = ttk.Combobox(inputFrame, width=28, state="readonly")
    eventDropDown = ttk.Combobox(inputFrame, width=32, state="readonly")
    statusDropDown = ttk.Combobox(inputFrame, width=15, state="readonly")

    scoutDropDown.grid(row=1, column=0, padx=5, pady=2)
    eventDropDown.grid(row=1, column=1, padx=5, pady=2)
    statusDropDown.grid(row=1, column=2, padx=5, pady=2)

    statusDropDown["values"] = ["Present", "Absent"]

    searchFrame = tk.Frame(parent)
    searchFrame.pack(pady=10)

    tk.Label(searchFrame, text="Search Attendance").grid(row=0, column=0, padx=5)

    searchEntry = tk.Entry(searchFrame)
    searchEntry.grid(row=0, column=1, padx=5)

    searchButton = tk.Button(searchFrame, text="Search", command=searchAttendanceRecords)
    searchButton.grid(row=0, column=2, padx=5)

    resetButton = tk.Button(searchFrame, text="Reset", command=resetSearch)
    resetButton.grid(row=0, column=3, padx=5)

    buttonFrame = tk.Frame(parent)
    buttonFrame.pack(pady=10)

    addButton = tk.Button(buttonFrame, text="Add Attendance", command=addAttendanceToDB)
    addButton.grid(row=0, column=0, padx=5)

    deleteButton = tk.Button(buttonFrame, text="Delete Selected Attendance", command=deleteSelectedAttendance)
    deleteButton.grid(row=0, column=1, padx=5)

    refreshButton = tk.Button(buttonFrame, text="Refresh Attendance", command=refreshAttendance)
    refreshButton.grid(row=0, column=2, padx=5)

    clearButton = tk.Button(buttonFrame, text="Clear Fields", command=clearAllInputs)
    clearButton.grid(row=0, column=3, padx=5)

    tableFrame = tk.Frame(parent)
    tableFrame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("Attendance ID", "First Name", "Last Name", "Event Name", "Event Date", "Status")

    scrollbar = tk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)

    scrollbar.config(command=tree.yview)

    for col in columns:
        tree.heading(col, text=col)

    tree.column("Attendance ID", width=100)
    tree.column("First Name", width = 120)
    tree.column("Last Name", width = 120)
    tree.column("Event Name", width = 180)
    tree.column("Event Date", width = 100)
    tree.column("Status", width = 100)

    loadScoutOptions()
    loadEventOptions()
    loadAttendance()


