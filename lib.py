import re

def getScoutIDFromSelection(selection):
        return int(selection.split(" - ")[0])

def getBadgeIDFromSelection(selection):
    return int(selection.split(" - ")[0])

#*************************************************ADAPTED CODE***************************************************
# https://blog.finxter.com/regex-match-dates/ adapted at 22/03/26
# adapted by swapping the parameters around, from YYYY/MM/DD to DD/MM/YYYY. changed the parameters for DD and MM to include both single and double digits to improve ease of access
# this code works by checking the number of characters in a specific format, and returns whether the input follows the rules in the form of true or false boolean states
def validDate(dateText):
    pattern = r"^\d{1,2}/\d{1,2}/\d{4}$"
    return re.match(pattern, dateText) is not None

#***************************************************ADAPTED CODE END**************************************************