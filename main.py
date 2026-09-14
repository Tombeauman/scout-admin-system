import tkinter as tk
from tkinter import ttk
from database import buildTables, addTestUser, seedReferenceData
from scoutDataGUI import createScoutPage
from eventGUI import createEventsPage
from attendanceGUI import createAttendancePage
from badgeRequirementsGUI import createBadgeRequirementPage
from badgeProgressGUI import createBadgeProgressPage
from patrolGUI import createPatrolsPage
from dashboardGUI import createDashboardPage
from loginGUI import showLogin
from userMgmtGUI import createUserPage


def startMainSystem(loggedInUser):
    gui = tk.Tk()
    gui.title("Scout Management System")
    gui.geometry("1000x800")

    def logout():
        gui.destroy()
        runProgram()

    topFrame = tk.Frame(gui)
    topFrame.pack(fill="x", pady=5)

    logoutButton = tk.Button(topFrame, text="Logout", command=logout)
    logoutButton.pack(side="right", padx=10)

    navi = ttk.Notebook(gui)
    navi.pack(fill="both", expand=True)

    dashboardPage = tk.Frame(navi)
    scoutPage = tk.Frame(navi)
    eventsPage = tk.Frame(navi)
    attendancePage = tk.Frame(navi)
    patrolPage = tk.Frame(navi)
    badgeRequirementsPage = tk.Frame(navi)
    badgeProgressPage = tk.Frame(navi)
    userMgmtPage = tk.Frame(navi)

    navi.add(dashboardPage, text="Dashboard")
    navi.add(scoutPage, text="Scout Data")
    navi.add(eventsPage, text="Events")
    navi.add(attendancePage, text="Attendance")
    navi.add(patrolPage, text="Patrol Management")
    navi.add(badgeRequirementsPage, text="Badge Requirements")
    navi.add(badgeProgressPage, text="Badge Progress")
    navi.add(userMgmtPage, text="User Management")

    createDashboardPage(dashboardPage, loggedInUser)
    createScoutPage(scoutPage, loggedInUser)
    createEventsPage(eventsPage, loggedInUser)
    createAttendancePage(attendancePage, loggedInUser)
    createPatrolsPage(patrolPage, loggedInUser)
    createBadgeRequirementPage(badgeRequirementsPage, loggedInUser)
    createBadgeProgressPage(badgeProgressPage, loggedInUser)
    createUserPage(userMgmtPage, loggedInUser)

    gui.mainloop()


def runProgram():
    loggedInUser = showLogin()

    if loggedInUser is None:
        return

    startMainSystem(loggedInUser)


buildTables()
seedReferenceData()
addTestUser()

runProgram()