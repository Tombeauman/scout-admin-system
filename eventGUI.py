import tkinter as tk
from tkinter import ttk, messagebox
from database import allEvents, addEvent, deleteEvent, searchEvent, updateEvent, getEventByID
from lib import validDate

selectedEventID = None

def createEventsPage(parent, loggedInUser):
    global tree, eventNameEntry, eventDateEntry, locationEntry, eventTypeEntry, descriptionEntry, nightsEntry, searchEntry

    currentUserID = loggedInUser[0]
    currentUserRole = loggedInUser[3]

#------------------functions------------------------------------

    # loads all the records from the table into the table interface
    def loadEvents():
        for row in tree.get_children():
            tree.delete(row)
            
        for event in allEvents():
            tree.insert("", tk.END, values=event)

    # clears the user's inputs from the input fields
    def clearInputs():
        eventNameEntry.delete(0, tk.END)
        eventDateEntry.delete(0, tk.END)
        locationEntry.delete(0, tk.END)
        eventTypeEntry.delete(0, tk.END)
        descriptionEntry.delete("1.0", tk.END)
        nightsEntry.delete(0, tk.END)
    
    # validates the user's inputs, ensuring required data exists for other functions
    def validateEventInput(eventName, eventDate, eventType, nights):
        if eventName.strip() == "" or eventDate.strip() == "" or eventType.strip() == "" or nights.strip() == "":
            messagebox.showerror("Input Error", "Event name, date, type, or number of nights is required.")
            return False    

        if not validDate(eventDate):
            messagebox.showerror("Input Error", "Event date must be inputted as DD/MM/YYYY.")
            return False

        if not nights.isdigit():
            messagebox.showerror("Input Error", "Nights must be a whole number.")
            return False

        return True

    # validates and adds the user's inputs to the event table
    def addEventToDB():
        eventName = eventNameEntry.get()
        eventDate = eventDateEntry.get()
        location = locationEntry.get()
        eventType = eventTypeEntry.get()
        description = descriptionEntry.get("1.0", tk.END).strip()
        nights = nightsEntry.get()

        if not validateEventInput(eventName, eventDate, eventType, nights):
            return

        addEvent(eventName, eventDate, location, eventType, description, int(nights), currentUserID)

        loadEvents()
        clearInputs()
        messagebox.showinfo("Success", "Event added successfully.")

    # deletes the selected event from the table, outputs an error if none are selected
    def deleteSelectedEvent():
        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select an event to delete.")
            return

        chosenEvent = tree.item(chosen[0])
        recordValues = chosenEvent["values"]
        eventID = recordValues[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete event ID {eventID}?"
        )

        if confirm:
            deleteEvent(eventID)
            loadEvents()
            messagebox.showinfo("Success", "Event deleted successfully.")

    # searches the table for a specified record
    def searchEventRecords():
        searchInput = searchEntry.get()

        for row in tree.get_children():
            tree.delete(row)

        results = searchEvent(searchInput)

        for event in results:
            tree.insert("", tk.END, values=event)

    # resets the search input field and refreshes the table
    def resetSearch():
        searchEntry.delete(0, tk.END)
        loadEvents()

    # loads the selected event into the input fields, so they can be updated
    def loadSelectedEvent():
        global selectedEventID

        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select an event to edit.")
            return

        chosenEvent = tree.item(chosen[0])
        recordValues = chosenEvent["values"]
        selectedEventID = int(recordValues[0])

        fullEvent = getEventByID(selectedEventID)

        clearInputs()

        eventNameEntry.insert(0, fullEvent[1])
        eventDateEntry.insert(0, fullEvent[2])
        locationEntry.insert(0, fullEvent[3])
        eventTypeEntry.insert(0, fullEvent[4])
        descriptionEntry.insert("1.0", fullEvent[5])
        nightsEntry.insert(0, fullEvent[6])

    # updates the selected event with the inputted values, outputs an error if none are selected
    def updateSelectedEvent():
        global selectedEventID

        if selectedEventID is None:
            messagebox.showerror("Update Error", "Please select an event record first.")
            return

        eventName = eventNameEntry.get()
        eventDate = eventDateEntry.get()
        location = locationEntry.get()
        eventType = eventTypeEntry.get()
        description = descriptionEntry.get("1.0", tk.END).strip()
        nights = nightsEntry.get()

        if not validateEventInput(eventName, eventDate, eventType, nights):
            return

        updateEvent(selectedEventID, eventName, eventDate, location, eventType, description, int(nights), currentUserID) 

        loadEvents()
        clearInputs()
        selectedEventID = None
        messagebox.showinfo("Success", "Event updated successfully.")

#-------------page layout----------------------

    titleLabel = tk.Label(parent, text="Event Records", font=("Arial", 16))
    titleLabel.pack(pady=10)

    roleLabel = tk.Label(parent, text=f"Logged in as: {loggedInUser[1]} ({currentUserRole})", font=("Arial", 10))
    roleLabel.pack(pady=2)

    inputFrame = tk.Frame(parent)
    inputFrame.pack(pady=10)

    tk.Label(inputFrame, text="Event Name").grid(row=0, column=0, padx=5, pady=2)
    tk.Label(inputFrame, text="Event Date").grid(row=0, column=1, padx=5, pady=2)
    tk.Label(inputFrame, text="Location").grid(row=0, column=2, padx=5, pady=2)
    tk.Label(inputFrame, text="Event Type").grid(row=0, column=3, padx=5, pady=2)
    tk.Label(inputFrame, text="Nights").grid(row=0, column=4, padx=5, pady=2)

    eventNameEntry = tk.Entry(inputFrame, width=18)
    eventDateEntry = tk.Entry(inputFrame, width=12)
    locationEntry = tk.Entry(inputFrame, width=18)
    eventTypeEntry = tk.Entry(inputFrame, width=15)
    nightsEntry = tk.Entry(inputFrame, width=8)

    eventNameEntry.grid(row=1, column=0, padx=5, pady=2)
    eventDateEntry.grid(row=1, column=1, padx=5, pady=2)
    locationEntry.grid(row=1, column=2, padx=5, pady=2)
    eventTypeEntry.grid(row=1, column=3, padx=5, pady=2)
    nightsEntry.grid(row=1, column=4, padx=5, pady=2)

    tk.Label(inputFrame, text="Description").grid(row=2, column=0, columnspan=5, pady=(10, 2))

    descriptionEntry = tk.Text(inputFrame, width=70, height=4)
    descriptionEntry.grid(row=3, column=0, columnspan=5, padx=5, pady=2)

    searchFrame = tk.Frame(parent)
    searchFrame.pack(pady=10)

    tk.Label(searchFrame, text="Search Event").grid(row=0, column=0, padx=5)

    searchEntry = tk.Entry(searchFrame)
    searchEntry.grid(row=0, column=1, padx=5)

    searchButton = tk.Button(searchFrame, text="Search", command=searchEventRecords)
    searchButton.grid(row=0, column=2, padx=5)

    resetButton = tk.Button(searchFrame, text="Reset", command=resetSearch)
    resetButton.grid(row=0, column=3, padx=5)

    buttonFrame = tk.Frame(parent)
    buttonFrame.pack(pady=10)

    addButton = tk.Button(buttonFrame, text="Add Event", command=addEventToDB)
    addButton.grid(row=0, column=0, padx=5)

    deleteButton= tk.Button(buttonFrame, text="Delete Event", command=deleteSelectedEvent)
    deleteButton.grid(row=0, column=1, padx=5)

    refreshButton = tk.Button(buttonFrame, text="Refresh Events", command=loadEvents)
    refreshButton.grid(row=0, column=2, padx=5)

    loadButton = tk.Button(buttonFrame, text="Load Selected Event", command=loadSelectedEvent)
    loadButton.grid(row=0, column=3, padx=5)

    updateButton = tk.Button(buttonFrame, text="Update Selected Event", command=updateSelectedEvent)
    updateButton.grid(row=0, column=4, padx=5)

    tableFrame = tk.Frame(parent)
    tableFrame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("Event ID", "Event Name", "Event Date", "Location", "Event Type", "Nights", "User ID")

    scrollbar = tk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)

    scrollbar.config(command=tree.yview)

    for col in columns:
        tree.heading(col, text=col)

    tree.column("Event ID", width=70)
    tree.column("Event Name", width=160)
    tree.column("Event Date", width=100)
    tree.column("Location", width=140)
    tree.column("Event Type", width=120)
    tree.column("Nights", width=70)
    tree.column("User ID", width=70)

    loadEvents()


      


            
