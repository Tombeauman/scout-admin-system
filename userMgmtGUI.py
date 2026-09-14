import tkinter as tk
from tkinter import ttk, messagebox
from database import allUsers, searchUsers, addUser, updateUser, deleteUser, updateUserPassword

selectedUserID = None

def createUserPage(parent, loggedInUser):
    global tree, usernameEntry, passwordEntry, roleDropDown, searchEntry

    currentUserRole = loggedInUser[3]
 
#--------------------------------------------------
# GUI functions

    def loadUsers():
        for row in tree.get_children():
            tree.delete(row)

        for user in allUsers():
            tree.insert("", tk.END, values=user)

    def clearInputs():
        usernameEntry.delete(0, tk.END)
        passwordEntry.delete(0, tk.END)
        roleDropDown.set("")

    def validateUserInput(username, role, passwordRequired=False):
        if username.strip() == "" or role.strip() == "":
            messagebox.showerror("Input Error", "Username and role are required.")
            return False

        if passwordRequired and passwordEntry.get().strip() == "":
            messagebox.showerror("Input Error", "Password is required for a new user.")
            return False

        return True

    def addUserToDB():
        username = usernameEntry.get()
        password = passwordEntry.get()
        role = roleDropDown.get()

        if not validateUserInput(username, role, passwordRequired=True):
            return

        try:
            addUser(username, password, role)
            loadUsers()
            clearInputs()
            messagebox.showinfo("Success", "User added successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def searchUserRecords():
        searchInput = searchEntry.get()

        for row in tree.get_children():
            tree.delete(row)

        results = searchUsers(searchInput)

        for user in results:
            tree.insert("", tk.END, values=user)

    def resetSearch():
        searchEntry.delete(0, tk.END)
        loadUsers()

    def loadSelectedUser():
        global selectedUserID

        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select a user to edit.")
            return

        chosenUser = tree.item(chosen[0])
        recordValues = chosenUser["values"]

        selectedUserID = recordValues[0]

        clearInputs()
        usernameEntry.insert(0, recordValues[1])
        roleDropDown.set(recordValues[2])

    def updateSelectedUser():
        global selectedUserID

        if selectedUserID is None:
            messagebox.showerror("Update Error", "Please select a user record first.")
            return

        username = usernameEntry.get()
        role = roleDropDown.get()
        newPassword = passwordEntry.get()

        if not validateUserInput(username, role):
            return

        try:
            updateUser(selectedUserID, username, role)

            if newPassword.strip() != "":
                updateUserPassword(selectedUserID, newPassword)

            loadUsers()
            clearInputs()
            selectedUserID = None
            messagebox.showinfo("Success", "User updated successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def deleteSelectedUser():
        chosen = tree.selection()

        if not chosen:
            messagebox.showerror("Selection Error", "Please select a user to delete.")
            return

        chosenUser = tree.item(chosen[0])
        recordValues = chosenUser["values"]
        userID = recordValues[0]
        username = recordValues[1]

        if userID == loggedInUser[0]:
            messagebox.showerror("Delete Error", "You cannot delete the account currently logged in.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?"
        )

        if confirm:
            try:
                deleteUser(userID)
                loadUsers()
                clearInputs()
                messagebox.showinfo("Success", "User deleted successfully.")
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

#------page layout-------------------

    titleLabel = tk.Label(parent, text="User Management", font=("Arial", 16))
    titleLabel.pack(pady=10)

    roleLabel = tk.Label(parent, text=f"Logged in as: {loggedInUser[1]} ({currentUserRole})", font=("Arial", 10))
    roleLabel.pack(pady=2)

    inputFrame = tk.Frame(parent)
    inputFrame.pack(pady=10)

    tk.Label(inputFrame, text="Username").grid(row=0, column=0, padx=5)
    tk.Label(inputFrame, text="Password").grid(row=0, column=1, padx=5)
    tk.Label(inputFrame, text="Role").grid(row=0, column=2, padx=5)

    usernameEntry = tk.Entry(inputFrame, width=20)
    passwordEntry = tk.Entry(inputFrame, width=20, show="*")
    roleDropDown = ttk.Combobox(inputFrame, width=18, state="readonly")
    roleDropDown["values"] = ["Admin", "Leader"]

    usernameEntry.grid(row=1, column=0, padx=5)
    passwordEntry.grid(row=1, column=1, padx=5)
    roleDropDown.grid(row=1, column=2, padx=5)

    searchFrame = tk.Frame(parent)
    searchFrame.pack(pady=10)

    tk.Label(searchFrame, text="Search User").grid(row=0, column=0, padx=5)

    searchEntry = tk.Entry(searchFrame)
    searchEntry.grid(row=0, column=1, padx=5)

    searchButton = tk.Button(searchFrame, text="Search", command=searchUserRecords)
    searchButton.grid(row=0, column=2, padx=5)

    resetButton = tk.Button(searchFrame, text="Reset", command=resetSearch)
    resetButton.grid(row=0, column=3, padx=5)

    buttonFrame = tk.Frame(parent)
    buttonFrame.pack(pady=10)

    addButton = tk.Button(buttonFrame, text="Add User", command=addUserToDB)
    addButton.grid(row=0, column=0, padx=5)

    deleteButton = tk.Button(buttonFrame, text="Delete Selected User", command=deleteSelectedUser)
    deleteButton.grid(row=0, column=1, padx=5)

    refreshButton = tk.Button(buttonFrame, text="Refresh Users", command=loadUsers)
    refreshButton.grid(row=0, column=2, padx=5)

    loadButton = tk.Button(buttonFrame, text="Load Selected User", command=loadSelectedUser)
    loadButton.grid(row=0, column=3, padx=5)

    updateButton = tk.Button(buttonFrame, text="Update User", command=updateSelectedUser)
    updateButton.grid(row=0, column=4, padx=5)

    clearButton = tk.Button(buttonFrame, text="Clear Fields", command=clearInputs)
    clearButton.grid(row=0, column=5, padx=5)

    tableFrame = tk.Frame(parent)
    tableFrame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("User ID", "Username", "Role")

    scrollbar = tk.Scrollbar(tableFrame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(tableFrame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)

    scrollbar.config(command=tree.yview)

    for col in columns:
        tree.heading(col, text=col)

    tree.column("User ID", width=100)
    tree.column("Username", width=180)
    tree.column("Role", width=120)

    if currentUserRole != "Admin":
        addButton.config(state="disabled")
        deleteButton.config(state="disabled")
        updateButton.config(state="disabled")

    loadUsers()
