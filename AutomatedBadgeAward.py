from datetime import datetime
from database import allScoutIDs, allRequirementRules, scoutAttendanceByType, badgeAlreadyAwarded, awardBadge, scoutNightsByType

# defines the original function, so it can be called in other files, such as the Badge Progress interface
def awardBadgeAuto():
    awardedCount = 0

    scouts = allScoutIDs()
    rules = allRequirementRules()

#*********ADAPTED CODE*****************************
# https://www.geeksforgeeks.org/python/python-strftime-function/
# adapted the answer by changing the format it is retrieved in and the variable it's stored in
# used to get the current time of when the badge is automatically awarded

    today = datetime.now().strftime("%d/%m/%y")

    for scout in scouts:
        scoutID = scout[0]

        for rule in rules:
            requirementID, badgeID, requiredAttendance, eventType, otherCriteria = rule

            if otherCriteria == "Nights":
                progressValue = scoutNightsByType(scoutID, eventType)
            else:
                progressValue = scoutAttendanceByType(scoutID, eventType)

            if progressValue >= requiredAttendance:
               if not badgeAlreadyAwarded(scoutID, badgeID):
                   awardBadge(scoutID, badgeID, today, "Auto")
                   awardedCount = awardedCount + 1

    return awardedCount
    

