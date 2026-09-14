import tkinter as tk
from tkinter import ttk, messagebox
from database import allBadgeProgress, deleteBadgeProgress, searchBadgeProgress, scoutList, badgeList, awardBadge, badgeAlreadyAwarded
from AutomatedBadgeAward import awardBadgeAuto
from datetime import datetime
from lib import getScoutIDFromSelection, getBadgeIDFromSelection

# allows the GUI and it's functions to be built and used when called
def createBadgeProgressPage(parent, loggedInUser):
    global tree, searchEntry

    currentUserRole = loggedInUser[3]

    # loads the records into the table interface
    def loadBadgeProgress():
        for row in tree.get_children():
            tree.delete(row)

        for record in allBadgeProgress():
            tree.insert("", tk.END, values=record)

    # searches the badge progress records by the inputted search field
    def searchProgressRecords():
        searchInput = searchEntry.get()

        for row in tree.get_children():
            tree.delete(row)

        results = searchBadgeProgress(searchInput)

        for record in results:
            tree.insert("", tk.END, values=record)

    # resets the search input field, and refreshes the table interface
    def resetSearch():
        searchEntry.delete(0, tk.END)
        loadBadgeProgress()

    # removes the selected record from the table, outputs an error if no record is chosen
    def deleteSelectedProgress():
        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select a badge progress record to delete.")
            return

        chosenRecord = tree.item(chosen[0])
        recordValues = chosenRecord["values"]
        progressID = recordValues[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete progress ID {progressID}?"
        )

        if confirm:
            deleteBadgeProgress(progressID)
            loadBadgeProgress()
            messagebox.showinfo("Success", "Badge progress record deleted successfully.")
    
    # loads and executes the automated badge awarding system in the GUI, then outputs a confirmation message
    def runAutoAwardFromGUI():
        awarded = awardBadgeAuto()
        loadBadgeProgress()
        messagebox.showinfo("Automation Complete", f"{awarded} badge(s) were awarded automatically.")

    def loadScoutOptions():
        scouts = scoutList()
        scoutOptions = [f"{scout[0]} - {scout[2]}, {scout[1]}" for scout in scouts]
        scoutDropdown["values"] = scoutOptions

    def loadBadgeOptions():
        badges = badgeList()
        badgeOptions = [f"{badge[0]} - {badge[1]}" for badge in badges]
        badgeDropdown["values"] = badgeOptions

    def awardManualBadge():
        scoutSelection = scoutDropdown.get()
        badgeSelection = badgeDropdown.get()

        if scoutSelection == "" or badgeSelection == "":
            messagebox.showerror("Selection Error", "Please select a scout and a badge.")
            return
        
        scoutID = getScoutIDFromSelection(scoutSelection)
        badgeID = getBadgeIDFromSelection(badgeSelection)
        today = datetime.now().strftime("%d/%m/%y")

        if badgeAlreadyAwarded(scoutID, badgeID):
           messagebox.showerror("Award Error", "This scout has already been awarded that badge.")
           return

        awardBadge(scoutID, badgeID, today, "Manual")
        loadBadgeProgress()
        scoutDropdown.set("")
        badgeDropdown.set("")
        messagebox.showinfo("Success", "Badge awarded successfully.")

#----------------------------------------------------------------------------------
# GUI badgeProgress initialisation

    titleLabel = tk.Label(parent, text="Badge Progress", font=("Arial", 16))
    titleLabel.pack(pady=10)

    roleLabel = tk.Label(parent, text=f"Logged in as: {loggedInUser[1]} ({currentUserRole})", font=("Arial", 10))
    roleLabel.pack(pady=2)

    searchFrame = tk.Frame(parent)
    searchFrame.pack(pady=10)

    tk.Label(searchFrame, text="Search Badge Progress").grid(row=0, column=0, padx=5)

    searchEntry = tk.Entry(searchFrame)
    searchEntry.grid(row=0, column=1, padx=5)

    searchButton = tk.Button(searchFrame, text="Search", command=searchProgressRecords)
    searchButton.grid(row=0, column=2, padx=5)

    resetButton = tk.Button(searchFrame, text="Reset Search", command=resetSearch)
    resetButton.grid(row=0, column=3, padx=5)

    manualFrame = tk.Frame(parent)
    manualFrame.pack(pady=10)

    tk.Label(manualFrame, text="Scout").grid(row=0, column=0, padx=5)
    tk.Label(manualFrame, text="Badge").grid(row=0, column=1, padx=5)

    scoutDropdown = ttk.Combobox(manualFrame, width=28, state="readonly")   
    scoutDropdown.grid(row=1, column=0, padx=5)

    badgeDropdown = ttk.Combobox(manualFrame, width=25, state="readonly")
    badgeDropdown.grid(row=1, column=1, padx=5)

    manualAwardButton = tk.Button(manualFrame, text="Award Badge Manually", command=awardManualBadge)
    manualAwardButton.grid(row=1, column=2, padx=10)

    buttonFrame = tk.Frame(parent)
    buttonFrame.pack(pady=10)

    runButton = tk.Button(buttonFrame, text="Run Badge Automation", command=runAutoAwardFromGUI)
    runButton.grid(row=0, column=0, padx=5)

    deleteButton = tk.Button(buttonFrame, text="Delete Selected Progress", command=deleteSelectedProgress)
    deleteButton.grid(row=0, column=1, padx=5)

    refreshButton = tk.Button(buttonFrame, text="Refresh Progress", command=loadBadgeProgress)
    refreshButton.grid(row=0, column=2, padx=5)

    if currentUserRole != "Admin":
       runButton.config(state="disabled")
       deleteButton.config(state="disabled")

    tableFrame = tk.Frame(parent)
    tableFrame.pack(fill="both", expand=True, padx=5, pady=10)

    columns = ("Progress ID", "First Name", "Last Name", "Badge Name", "Date Awarded", "Award Method")

    scrollbar = tk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)

    scrollbar.config(command=tree.yview)

    for col in columns:
        tree.heading(col, text=col)

    tree.column("Progress ID", width=100)
    tree.column("First Name", width=120)
    tree.column("Last Name", width=120)
    tree.column("Badge Name", width=150)
    tree.column("Date Awarded", width=100)
    tree.column("Award Method", width=100)

    loadBadgeOptions()
    loadScoutOptions()
    loadBadgeProgress()