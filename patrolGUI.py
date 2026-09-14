import tkinter as tk
from tkinter import ttk, messagebox
from database import allPatrols, addPatrol, deletePatrol, updatePatrol, searchPatrol

selectedPatrolID = None

def createPatrolsPage(parent, loggedInUser):
    global tree, patrolNameEntry, searchEntry

    currentUserRole = loggedInUser[3]

    # ---------------- functions ----------------

    def loadPatrols():
        for row in tree.get_children():
            tree.delete(row)

        for patrol in allPatrols():
            tree.insert("", tk.END, values=patrol)

    def clearInputs():
        patrolNameEntry.delete(0, tk.END)

    def addPatrolToDB():
        patrolName = patrolNameEntry.get()

        if patrolName.strip() == "":
            messagebox.showerror("Input Error", "Patrol name is required.")
            return

        addPatrol(patrolName)
        loadPatrols()
        clearInputs()
        messagebox.showinfo("Success", "Patrol added successfully.")

    def deleteSelectedPatrol():
        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select a patrol to delete.")
            return

        chosenPatrol = tree.item(chosen[0])
        recordValues = chosenPatrol["values"]
        patrolID = recordValues[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Patrol ID {patrolID}?"
        )

        if confirm:
            deletePatrol(patrolID)
            loadPatrols()
            clearInputs()
            messagebox.showinfo("Success", "Patrol deleted successfully.")

    def searchPatrolRecords():
        searchInput = searchEntry.get()

        for row in tree.get_children():
            tree.delete(row)

        results = searchPatrol(searchInput)

        for patrol in results:
            tree.insert("", tk.END, values=patrol)

    def resetSearch():
        searchEntry.delete(0, tk.END)
        loadPatrols()

    def loadSelectedPatrol():
        global selectedPatrolID

        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select a patrol to edit.")
            return

        chosenPatrol = tree.item(chosen[0])
        recordValues = chosenPatrol["values"]

        selectedPatrolID = recordValues[0]

        clearInputs()
        patrolNameEntry.insert(0, recordValues[1])

    def updateSelectedPatrol():
        global selectedPatrolID

        if selectedPatrolID is None:
            messagebox.showerror("Update Error", "Please select a patrol record first.")
            return

        patrolName = patrolNameEntry.get()

        if patrolName.strip() == "":
            messagebox.showerror("Input Error", "Patrol name is required.")
            return

        updatePatrol(selectedPatrolID, patrolName)
        loadPatrols()
        clearInputs()
        selectedPatrolID = None
        messagebox.showinfo("Success", "Patrol updated successfully.")

    # ---------------- page layout ----------------

    titleLabel = tk.Label(parent, text="Patrol Management", font=("Arial", 16))
    titleLabel.pack(pady=10)

    roleLabel = tk.Label(parent, text=f"Logged in as: {loggedInUser[1]} ({currentUserRole})", font=("Arial", 10))
    roleLabel.pack(pady=2)

    inputFrame = tk.Frame(parent)
    inputFrame.pack(pady=10)

    tk.Label(inputFrame, text="Patrol Name").grid(row=0, column=0, padx=5)
    patrolNameEntry = tk.Entry(inputFrame, width=25)
    patrolNameEntry.grid(row=1, column=0, padx=5)

    searchFrame = tk.Frame(parent)
    searchFrame.pack(pady=10)

    tk.Label(searchFrame, text="Search Patrol").grid(row=0, column=0, padx=5)

    searchEntry = tk.Entry(searchFrame)
    searchEntry.grid(row=0, column=1, padx=5)

    searchButton = tk.Button(searchFrame, text="Search", command=searchPatrolRecords)
    searchButton.grid(row=0, column=2, padx=5)

    resetButton = tk.Button(searchFrame, text="Reset", command=resetSearch)
    resetButton.grid(row=0, column=3, padx=5)

    buttonFrame = tk.Frame(parent)
    buttonFrame.pack(pady=10)

    addButton = tk.Button(buttonFrame, text="Add Patrol", command=addPatrolToDB)
    addButton.grid(row=0, column=0, padx=5)

    deleteButton = tk.Button(buttonFrame, text="Delete Selected Patrol", command=deleteSelectedPatrol)
    deleteButton.grid(row=0, column=1, padx=5)

    refreshButton = tk.Button(buttonFrame, text="Refresh Patrols", command=loadPatrols)
    refreshButton.grid(row=0, column=2, padx=5)

    loadButton = tk.Button(buttonFrame, text="Load Selected Patrol", command=loadSelectedPatrol)
    loadButton.grid(row=0, column=3, padx=5)

    updateButton = tk.Button(buttonFrame, text="Update Patrol", command=updateSelectedPatrol)
    updateButton.grid(row=0, column=4, padx=5)

    clearButton = tk.Button(buttonFrame, text="Clear Fields", command=clearInputs)
    clearButton.grid(row=0, column=5, padx=5)

    if currentUserRole != "Admin":
       deleteButton.config(state="disabled")

    tableFrame = tk.Frame(parent)
    tableFrame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("Patrol ID", "Patrol Name", "Leader Scout ID")

    scrollbar = tk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)

    scrollbar.config(command=tree.yview)

    for col in columns:
        tree.heading(col, text=col)

    tree.column("Patrol ID", width=100)
    tree.column("Patrol Name", width=180)
    tree.column("Leader Scout ID", width=120)

    loadPatrols()
