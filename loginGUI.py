import tkinter as tk
from tkinter import messagebox
from database import checkLogin

#-------------------------------------------
# login functions for the GUI

# allows the user login to be called by main.py when the program is executed
def showLogin():
        loggedInUser = {"user": None}

        # authenticates the user's inputs by checking them against the table
        def tryLogin():
            username = usernameEntry.get()
            password = passwordEntry.get()

            user = checkLogin(username, password)

            if user is None:
                messagebox.showerror("Login Failed", "The username or password is incorrect.")
                return

            loggedInUser["user"] = user
            loginWindow.destroy()

#-------------------------------------------------------------
# GUI initialisation for the login interface

        loginWindow = tk.Tk()
        loginWindow.title("Login")
        loginWindow.geometry("300x200")

        tk.Label(loginWindow, text="Scout Management Login", font=("Arial", 12)).pack(pady=10)

        tk.Label(loginWindow, text="Username").pack()
        usernameEntry = tk.Entry(loginWindow)
        usernameEntry.pack(pady=5)

        tk.Label(loginWindow, text="Password").pack()
        passwordEntry = tk.Entry(loginWindow, show="*")
        passwordEntry.pack(pady=5)

        loginButton = tk.Button(loginWindow, text="Login", command=tryLogin)
        loginButton.pack(pady=10)

        loginWindow.mainloop()

        return loggedInUser["user"]


