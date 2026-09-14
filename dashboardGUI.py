import tkinter as tk
from database import totalScouts, totalEvents, totalAttendanceRecords, totalBadgesAwarded, recentBadgeAwards

def createDashboardPage(parent, loggedInUser):

    currentUserRole = loggedInUser[3]

#---------function(s)--------------

    def loadDashboard():
        scoutCountLabel.config(text=f"Total Scouts: {totalScouts()}")
        eventCountLabel.config(text=f"Total Events: {totalEvents()}")
        attendanceCountLabel.config(text=f"Attendance Records: {totalAttendanceRecords()}")
        badgeCountLabel.config(text=f"Badges Awarded: {totalBadgesAwarded()}")

        recentList.delete(0, tk.END)

#--------------GUI layout / generation-----------

        for award in recentBadgeAwards():
            firstName, lastName, badgeName, dateAwarded, awardMethod = award
            recentList.insert(tk.END, f"{firstName} {lastName} - {badgeName} ({dateAwarded}, {awardMethod})")

    titleLabel = tk.Label(parent, text="Dashboard", font=("Arial", 16))
    titleLabel.pack(pady=15)

    roleLabel = tk.Label(parent, text=f"Logged in as: {loggedInUser[1]} ({currentUserRole})", font=("Arial", 10))
    roleLabel.pack(pady=2)

    statsOuterFrame = tk.Frame(parent, bd=1, relief="solid", padx=20, pady=15)
    statsOuterFrame.pack(pady=10)

    scoutCountLabel = tk.Label(statsOuterFrame, text="Total Scouts: 0", font=("Arial", 12), width=22, anchor="w")
    scoutCountLabel.grid(row=0, column=0, padx=15, pady=8)

    eventCountLabel = tk.Label(statsOuterFrame, text="Total Events: 0", font=("Arial", 12), width=22, anchor="w")
    eventCountLabel.grid(row=0, column=1, padx=15, pady=8)

    attendanceCountLabel = tk.Label(statsOuterFrame, text="Attendance Records: 0", font=("Arial", 12), width=22, anchor="w")
    attendanceCountLabel.grid(row=1, column=0, padx=15, pady=8)

    badgeCountLabel = tk.Label(statsOuterFrame, text="Badges Awarded: 0", font=("Arial", 12), width=22, anchor="w")
    badgeCountLabel.grid(row=1, column=1, padx=15, pady=8)

    recentOuterFrame = tk.Frame(parent, bd=1, relief="solid", padx=15, pady=10)
    recentOuterFrame.pack(pady=15)

    recentTitleLabel = tk.Label(recentOuterFrame, text="Recent Badge Awards", font=("Arial", 12))
    recentTitleLabel.pack(pady=(0, 10))

    recentList = tk.Listbox(recentOuterFrame, width=75, height=10)
    recentList.pack()

    refreshButton = tk.Button(parent, text="Refresh Dashboard", command=loadDashboard)
    refreshButton.pack(pady=10)

    loadDashboard()