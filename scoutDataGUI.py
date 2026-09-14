import tkinter as tk
from tkinter import ttk, messagebox
from database import allScouts, addScout, deleteScout, searchScout, updateScout, patrolList, bulkUpdateScoutPatrol, filterScoutsByPatrol, latestScout
from collections import deque
from lib import validDate

selectedScoutID = None

def createScoutPage(parent, loggedInUser):
    global tree, firstNameEntry, lastNameEntry, dobEntry, contactEntry, medInfoEntry, searchEntry
    
    currentUserRole = loggedInUser[3]
    actionQueue = deque(maxlen=5)

# --------------------------------------functions-----------------------------------------------------------------

   # rebuilds the table when called, showing any changes to data
    def loadScouts():
        for row in tree.get_children():
            tree.delete(row)

        for scout in allScouts():
            tree.insert("", tk.END, values=safeRow(scout))


    # trims the sensitive fields out of a scout record for non-admin users
    def safeRow(scout):
        if currentUserRole == "Admin":
            return scout
        return (scout[0], scout[1], scout[2], scout[3], scout[6])

    def clearInputs():
        firstNameEntry.delete(0, tk.END)
        lastNameEntry.delete(0, tk.END)
        dobEntry.delete(0, tk.END)
        contactEntry.delete(0, tk.END)
        medInfoEntry.delete(0, tk.END)

   # removes spaces in the input, then checks if characters exist. if none exist, a error message appears
    def validateScoutInput(firstName, lastName, dob):
         if firstName.strip() == "" or lastName.strip() == "" or dob.strip() == "":
             messagebox.showerror("Input Error", "First name, last name, or date of birth are required.")
             return False

         if not validDate(dob):
             messagebox.showerror("Input Error", "Date of birth must be in the format DD/MM/YYYY.")
             return False

         return True

    # adds a scout using the values entered into the input boxes by the user
    def addScoutToDB():
         firstName = firstNameEntry.get()
         lastName = lastNameEntry.get()
         dob = dobEntry.get()

         if currentUserRole == "Admin":
           parentContact = contactEntry.get()
           medInfo = medInfoEntry.get()
         else:
           parentContact = ""
           medInfo = ""

         if not validateScoutInput(firstName, lastName, dob):
             return

         addScout(firstName, lastName, dob, parentContact, medInfo, None)

         loadScouts()

         newestScout = latestScout()
         scoutID = newestScout[0]

         logScoutAction("ADD", scoutID, firstName, lastName)

         clearInputs()
         messagebox.showinfo("Success", "Scout added successfully.")

    # deletes the selected scout using ScoutID from the selected row, as stored in scoutID, with the selected record's values being stored in recordValues
    def deleteSelectedScout():
         chosen = tree.selection()

         if not chosen:
             messagebox.showerror("Selection Error", "Please select a scout to delete.")
             return

         chosenScout = tree.item(chosen[0])
         recordValues = chosenScout["values"]
         scoutID = recordValues[0]

         confirm = messagebox.askyesno(
             "Confirm Delete",
             f"Are you sure you want to delete Scout ID {scoutID}?"
         )
 
         if confirm:
             firstName = recordValues[1]
             lastName = recordValues[2]

             logScoutAction("DELETE", scoutID, firstName, lastName)

             deleteScout(scoutID)
             loadScouts()
             messagebox.showinfo("Success", "Scout deleted successfully.")

    # searches for scouts by first or last name
    def searchScoutRecords():
        searchInput = searchEntry.get()

        for row in tree.get_children():
            tree.delete(row)

        for scout in searchScout(searchInput):
            tree.insert("", tk.END, values=safeRow(scout))

    # resets the search box and reloads all scouts in the original format, organised by scoutID
    def resetSearch():
         searchEntry.delete(0, tk.END)
         loadScouts()

    # loads the selected scout's scoutID into a global variable, then wipes the current input fields and adds the selected record's info
    def loadSelectedScout():
         global selectedScoutID

         chosen = tree.selection()
 
         if not chosen:
             messagebox.showerror("Selection Error", "Please select a scout to edit.")
             return

         chosenScout = tree.item(chosen[0])
         recordValues = chosenScout["values"]

         selectedScoutID = recordValues[0] 

         clearInputs()

         firstNameEntry.insert(0, recordValues[1])
         lastNameEntry.insert(0, recordValues[2])
         dobEntry.insert(0, recordValues[3])

         if currentUserRole == "Admin":
           contactEntry.config(state="normal")
           medInfoEntry.config(state="normal")
           contactEntry.insert(0, recordValues[4])
           medInfoEntry.insert(0, recordValues[5])

         if currentUserRole != "Admin":
            contactEntry.config(state="disabled")
            medInfoEntry.config(state="disabled")

    # writes the inputted data to a variable, validates the inputs, then updates the selected records and wipes the entry boxes
    def updateSelectedScout():
         global selectedScoutID

         if selectedScoutID is None:
             messagebox.showerror("Update Error", "Please select a scout record first.")
             return
 
         firstName = firstNameEntry.get()
         lastName = lastNameEntry.get()
         dob = dobEntry.get()

         if currentUserRole == "Admin":
            parentContact = contactEntry.get()
            medInfo = medInfoEntry.get()
         else:
            parentContact = ""
            medInfo = ""

         if not validateScoutInput(firstName, lastName, dob):
             return

         updateScout(selectedScoutID, firstName, lastName, dob, parentContact, medInfo)

         logScoutAction("UPDATE", selectedScoutID, firstName, lastName)

         loadScouts()
         messagebox.showinfo("Success", "Scout updated successfully.")
         clearInputs()
         selectedScoutID = None

    def loadPatrolOptions():
        patrols = patrolList()
        patrolOptions = [f"{patrol[0]} - {patrol[1]}" for patrol in patrols]
        bulkPatrolDropdown["values"] = patrolOptions

    def getPatrolIDFromSelection(selection):
        return int(selection.split(" - ")[0])

    def bulkUpdatePatrol():
        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select one or more scouts.")
            return

        patrolSelection = bulkPatrolDropdown.get()

        if patrolSelection == "":
            messagebox.showerror("Input Error", "Please select a patrol.")
            return

        patrolID = getPatrolIDFromSelection(patrolSelection)

        scoutIDs = []
        for item in chosen:
            recordValues = tree.item(item)["values"]
            scoutIDs.append(recordValues[0])

        bulkUpdateScoutPatrol(scoutIDs, patrolID)
        loadScouts()
        bulkPatrolDropdown.set("")
        messagebox.showinfo("Success", "Selected scouts updated successfully.")

    def loadFilterPatrolOptions():
       patrols = patrolList()
       patrolOptions = [patrol[1] for patrol in patrols]
       filterPatrolDropdown["values"] = patrolOptions

    def applyPatrolFilter():
       patrolName = filterPatrolDropdown.get()

       if patrolName == "":
           messagebox.showerror("Filter Error", "Please select a patrol to filter by.")
           return

       for row in tree.get_children():
           tree.delete(row)

       for scout in filterScoutsByPatrol(patrolName):
           tree.insert("", tk.END, values=safeRow(scout))

    def clearPatrolFilter():
        filterPatrolDropdown.set("")
        loadScouts()

    def refreshScoutPage():
        loadPatrolOptions()
        loadFilterPatrolOptions()
        loadScouts()

#************ADAPTED CODE START**********************************
# https://www.geeksforgeeks.org/python/deque-in-python/
# https://www.geeksforgeeks.org/python/python-reversed-function/
# Adapted from the "Appending and Deleting Dequeue Items" example, changing the queue name and it's inputs
# used to store the user's most recent actions by adding the scout's name, ID and the action performed on their record
# then displaying that queue in a frame in the GUI. improves user understandability and minimises accidental inputs 
# note that the code defining the queue, actionQueue = deque(maxlen=10) is also adapted as well

    def refreshRecentActionQueueGUI():
       actionListbox.delete(0, tk.END)
       for action in reversed(actionQueue):
          actionType, scoutID, scoutName = action
          actionListbox.insert(tk.END, f"{actionType}: ID {scoutID} - {scoutName}")

    def logScoutAction(actionType, scoutID, firstName, lastName):
        actionQueue.append((actionType, scoutID, f"{firstName} {lastName}"))
        refreshRecentActionQueueGUI()

#***********ADAPTED CODE END*****************************

#------------------------------page layout------------------------------------------------------------

    titleLabel = tk.Label(parent, text="Scout Records", font=("Arial", 16))
    titleLabel.pack(pady=10)

    roleLabel = tk.Label(parent, text=f"Logged in as: {loggedInUser[1]} ({currentUserRole})", font=("Arial", 10))
    roleLabel.pack(pady=2)

    inputFrame = tk.Frame(parent)
    inputFrame.pack(pady=10)

    tk.Label(inputFrame, text="First Name").grid(row=0, column=0, padx=5)
    tk.Label(inputFrame, text="Last Name").grid(row=0, column=1, padx=5)
    tk.Label(inputFrame, text="Date of Birth").grid(row=0, column=2, padx=5)
    tk.Label(inputFrame, text="Parent Contact").grid(row=0, column=3, padx=5)
    tk.Label(inputFrame, text="Medical Info").grid(row=0, column=4, padx=5)

    firstNameEntry = tk.Entry(inputFrame)
    lastNameEntry = tk.Entry(inputFrame)
    dobEntry = tk.Entry(inputFrame)
    contactEntry = tk.Entry(inputFrame)
    medInfoEntry = tk.Entry(inputFrame)

    if currentUserRole != "Admin":
      contactEntry.config(state="disabled")
      medInfoEntry.config(state="disabled")

    firstNameEntry.grid(row=1, column=0, padx=5)
    lastNameEntry.grid(row=1, column=1, padx=5)
    dobEntry.grid(row=1, column=2, padx=5)
    contactEntry.grid(row=1, column=3, padx=5)
    medInfoEntry.grid(row=1, column=4, padx=5)

    searchFrame = tk.Frame(parent)
    searchFrame.pack(pady=10)

    tk.Label(searchFrame, text="Search Scout").grid(row=0, column=0, padx=5)

    searchEntry = tk.Entry(searchFrame)
    searchEntry.grid(row=0, column=1, padx=5)

    searchButton = tk.Button(searchFrame, text="Search", command=searchScoutRecords)
    searchButton.grid(row=0, column=2, padx=5)
 
    resetButton = tk.Button(searchFrame, text="Reset", command=resetSearch)
    resetButton.grid(row=0, column=3, padx=5)

    filterFrame = tk.Frame(parent)
    filterFrame.pack(pady=10)

    tk.Label(filterFrame, text="Filter by Patrol").grid(row=0, column=0, padx=5)

    filterPatrolDropdown = ttk.Combobox(filterFrame, width=20, state="readonly")
    filterPatrolDropdown.grid(row=0, column=1, padx=5)

    applyFilterButton = tk.Button(filterFrame, text="Apply Filter", command=applyPatrolFilter)
    applyFilterButton.grid(row=0, column=2, padx=5)

    clearFilterButton = tk.Button(filterFrame, text="Clear Filter", command=clearPatrolFilter)
    clearFilterButton.grid(row=0, column=3, padx=5)

    buttonFrame = tk.Frame(parent)
    buttonFrame.pack(pady=10)

    addButton = tk.Button(buttonFrame, text="Add Scout", command=addScoutToDB)
    addButton.grid(row=0, column=0, padx=5)

    deleteButton = tk.Button(buttonFrame, text="Delete Selected Scout", command=deleteSelectedScout)
    deleteButton.grid(row=0, column=1, padx=5)

    refreshButton = tk.Button(buttonFrame, text="Refresh Scouts", command=refreshScoutPage)
    refreshButton.grid(row=0, column=2, padx=5)

    loadButton = tk.Button(buttonFrame, text="Load Selected Scout", command=loadSelectedScout)
    loadButton.grid(row=0, column=3, padx=5)

    updateButton = tk.Button(buttonFrame, text="Update Scout", command=updateSelectedScout)
    updateButton.grid(row=0, column=4, padx=5)

    clearButton = tk.Button(buttonFrame, text="Clear Fields", command=clearInputs)
    clearButton.grid(row=0, column=5, padx=5)

    if currentUserRole != "Admin":
      deleteButton.config(state="disabled")
      updateButton.config(state="disabled")

    bulkFrame = tk.Frame(parent)
    bulkFrame.pack(pady=10)

    tk.Label(bulkFrame, text="Bulk Update Patrol").grid(row=0, column=0, padx=5)

    bulkPatrolDropdown = ttk.Combobox(bulkFrame, width=20, state="readonly")
    bulkPatrolDropdown.grid(row=0, column=1, padx=5)

    bulkUpdateButton = tk.Button(bulkFrame, text="Apply to Selected Scouts", command=bulkUpdatePatrol)
    bulkUpdateButton.grid(row=0, column=2, padx=5)

    queueFrame = tk.Frame(parent)
    queueFrame.pack(pady=10)

    tk.Label(queueFrame, text="Recent Scout Actions").pack()

    actionListbox = tk.Listbox(queueFrame, width=50, height=5)
    actionListbox.pack()

    tableFrame = tk.Frame(parent)
    tableFrame.pack(fill="both", expand=True, padx=10, pady=10)

    if currentUserRole == "Admin":
       columns = ("Scout ID", "First Name", "Last Name", "Date Of Birth", "Parent Contact", "Medical Info", "Patrol Name")
    else:
        columns = ("Scout ID", "First Name", "Last Name", "Date Of Birth", "Patrol Name")

    scrollbar = tk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", selectmode="extended", yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)

    scrollbar.config(command=tree.yview)

    for col in columns:
       tree.heading(col, text=col)
       tree.column(col, width=130)

    loadPatrolOptions()
    loadFilterPatrolOptions()
    loadScouts()