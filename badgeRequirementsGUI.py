import tkinter as tk
from tkinter import messagebox, ttk
from database import addBadgeRequirement, allBadgeRequirements, deleteBadgeRequirement, searchBadgeRequirements, updateBadgeRequirement, badgeList
from lib import getBadgeIDFromSelection

selectedRequirementID = None

#----------------------------------------------------
# GUI functions

# function, which when called, makes badgeRequirements GUI
def createBadgeRequirementPage(parent, loggedInUser):
    global tree, badgeDropDown, requiredAttendanceEntry, eventTypeEntry, otherCriteriaEntry, searchEntry
    
    currentUserRole = loggedInUser[3]

    # clear the add function inputs
    def clearInputs():
        badgeDropDown.set("")
        requiredAttendanceEntry.delete(0, tk.END)
        eventTypeEntry.delete(0, tk.END)
        otherCriteriaEntry.delete(0, tk.END)

    # ensures data inputted by the user is not null for the required records for badge automation to function
    def validateRequirementInput(badgeSelection, requiredAttendance, eventType):
        if badgeSelection == "" or requiredAttendance.strip() == "" or eventType.strip() == "":
            messagebox.showerror("Input Error", "Badge, required attendance value and event type are required.")
            return False

        if not requiredAttendance.isdigit():
            messagebox.showerror("Input Error", "Required attendance must be a whole number.")
            return False
        return True

    # loads badge requirements, so they can be displayed in the table GUI
    def loadBadgeRequirements():
        for row in tree.get_children():
            tree.delete(row)

        for record in allBadgeRequirements():
            tree.insert("", tk.END, values=record)

    # resets the user's search fields, and refreshes the table GUI to display all records
    def resetSearch():
        searchEntry.delete(0, tk.END)
        loadBadgeRequirements()

    # adds a record to the table - uses validateRequirementInput to ensure required data exists
    # then calls getBadgeIDFromSelection so the associated badge can be stored along with the other info
    def addRequirementToDB():
        badgeSelection = badgeDropDown.get()
        requiredAttendance = requiredAttendanceEntry.get()
        eventType = eventTypeEntry.get()
        otherCriteria = otherCriteriaEntry.get()

        if not validateRequirementInput(badgeSelection, requiredAttendance, eventType):
            return

        badgeID = getBadgeIDFromSelection(badgeSelection)

        addBadgeRequirement(badgeID, int(requiredAttendance), eventType, otherCriteria)

        loadBadgeRequirements()
        clearInputs()
        messagebox.showinfo("Success", "Badge requirement added successfully.")

    # deletes the selected record from the table, then reloads the table
    def deleteSelectedRequirement():
        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select a requirement to delete.")
            return

        chosenRecord = tree.item(chosen[0])
        recordValues = chosenRecord["values"]
        requirementID = recordValues[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete requirement ID {requirementID}?"
        )

        if confirm:
            deleteBadgeRequirement(requirementID)
            loadBadgeRequirements()
            messagebox.showinfo("Success", "Badge requirement deleted successfully.")

    # searches the table for a record similar to the user's search query
    def searchRequirementRecords():
        searchInput = searchEntry.get()

        for row in tree.get_children():
            tree.delete(row)

        results = searchBadgeRequirements(searchInput)

        for record in results:
            tree.insert("", tk.END, values=record)

    # updates the selected record by the inputted fields
    def updateSelectedRequirement():
        global selectedRequirementID

        chosen = tree.selection()

        if selectedRequirementID is None:
            messagebox.showerror("Update Error", "Please select a requirement record first.")
            return

        badgeSelection = badgeDropDown.get()
        requiredAttendance = requiredAttendanceEntry.get()
        eventType = eventTypeEntry.get()
        otherCriteria = otherCriteriaEntry.get()

        if not validateRequirementInput(badgeSelection, requiredAttendance, eventType):
            return

        badgeID = getBadgeIDFromSelection(badgeSelection)

        updateBadgeRequirement(selectedRequirementID, badgeID, int(requiredAttendance), eventType, otherCriteria)

        loadBadgeRequirements()
        clearInputs()
        selectedRequirementID = None
        messagebox.showinfo("Success", "Requirement updated succesfully.")

    # stores the available badges to be displayed in the dropdown tab
    def loadBadgeOptions():
        badges = badgeList()
        badgeOptions = [f"{badge[0]} - {badge[1]}" for badge in badges]
        badgeDropDown["values"] = badgeOptions

    # searches the badgeList for a name equivalent to the inputted badge name
    def findBadgeSelectionByName(badgeName):
        badges = badgeList()
        for badge in badges:
            if badge[1] == badgeName:
                return f"{badge[0]} - {badge[1]}"
        return ""

    # loads the selected badge requirement record into the input fields, so they can be updated
    def loadSelectedRequirement():
        global selectedRequirementID

        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select a requirement to edit.")
            return

        chosenRecord  = tree.item(chosen[0])
        recordValues = chosenRecord["values"]

        selectedRequirementID = recordValues[0]

        clearInputs()

        badgeDropDown.set(findBadgeSelectionByName(recordValues[1])) 
        requiredAttendanceEntry.insert(0, recordValues[2])
        eventTypeEntry.insert(0, recordValues[3])   

        if recordValues[4] is not None:
            otherCriteriaEntry.insert(0, recordValues[4])

    #---------------------------------------------------
    # GUI initialisation

    titleLabel = tk.Label(parent, text="Badge Requirements", font=("Arial", 16))
    titleLabel.pack(pady=10)

    roleLabel = tk.Label(parent, text=f"Logged in as: {loggedInUser[1]} ({currentUserRole})", font=("Arial", 10))
    roleLabel.pack(pady=2)

    inputFrame = tk.Frame(parent)
    inputFrame.pack(pady=10)

    tk.Label(inputFrame, text="Badge").grid(row=0, column=0, padx=5, pady=2)
    tk.Label(inputFrame, text="Required Attendance").grid(row=0, column=1, padx=5, pady=2)
    tk.Label(inputFrame, text="Event Type").grid(row=0, column=2, padx=5, pady=2)
    tk.Label(inputFrame, text="Other Criteria").grid(row=0, column=3, padx=5, pady=2)

    badgeDropDown = ttk.Combobox(inputFrame, width=25, state="readonly")
    requiredAttendanceEntry = tk.Entry(inputFrame, width=18)
    eventTypeEntry = tk.Entry(inputFrame, width=18)
    otherCriteriaEntry = tk.Entry(inputFrame, width=25)

    badgeDropDown.grid(row=1, column=0, padx=5, pady=2)
    requiredAttendanceEntry.grid(row=1, column=1, padx=5, pady=2)
    eventTypeEntry.grid(row=1, column=2, padx=5, pady=2)
    otherCriteriaEntry.grid(row=1, column=3, padx=5, pady=3)

    searchFrame = tk.Frame(parent)
    searchFrame.pack(pady=10)

    tk.Label(searchFrame, text="Search Requirements").grid(row=0, column=0, padx=5)

    searchEntry = tk.Entry(searchFrame)
    searchEntry.grid(row=0, column=1, padx=5)

    searchButton = tk.Button(searchFrame, text="Search", command=searchRequirementRecords)
    searchButton.grid(row=0, column=2, padx=5)

    resetButton = tk.Button(searchFrame, text="Reset", command=resetSearch)
    resetButton.grid(row=0, column=3, padx=5)

    buttonFrame = tk.Frame(parent)
    buttonFrame.pack(pady=10)

    addButton = tk.Button(buttonFrame, text="Add Requirement", command=addRequirementToDB)
    addButton.grid(row=0, column=0, padx=5)

    deleteButton = tk.Button(buttonFrame, text="Delete Selected Requirement", command=deleteSelectedRequirement)
    deleteButton.grid(row=0, column=1, padx=5)

    refreshButton = tk.Button(buttonFrame, text="Refresh Requirements", command=loadBadgeRequirements)
    refreshButton.grid(row=0, column=2, padx=5)

    loadButton = tk.Button(buttonFrame, text="Load Selected Requirement", command=loadSelectedRequirement)
    loadButton.grid(row=0, column=3, padx=5)

    updateButton = tk.Button(buttonFrame, text="Update Selected Requirement", command=updateSelectedRequirement)
    updateButton.grid(row=0, column=4, padx=5)

    clearButton = tk.Button(buttonFrame, text="Clear Input Fields", command=clearInputs)
    clearButton.grid(row=0, column=5, padx=5)

    tableFrame = tk.Frame(parent)
    tableFrame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("Requirement ID", "Badge Name", "Required Attendance", "Event Type", "Other Criteria")

    scrollbar = tk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)

    scrollbar.config(command=tree.yview)

    for col in columns:
        tree.heading(col, text=col)

    tree.column("Requirement ID", width=110)
    tree.column("Badge Name", width=150)
    tree.column("Required Attendance", width=140)
    tree.column("Event Type", width=120)
    tree.column("Other Criteria", width=180)

    loadBadgeOptions()
    loadBadgeRequirements()



