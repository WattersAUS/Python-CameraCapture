#
#  Module: general.py - G.J. Watson
#    Desc: general use routines
# Version: 1.01
#
import time

def getFormattedCurrentDateTime():
    dateStr = time.strftime("%Y%m%d-%H%M%S")
    return dateStr

def logMessage(iMessage):
    oMessage = '[' + getFormattedCurrentDateTime() + ']: ' + iMessage + '...'
    print(oMessage)
    return

def errMessage(eMessage):
    logMessage('ERROR: ' + eMessage)
    return

def debugMessage(eMessage):
    logMessage('DEBUG: ' + eMessage)
    return

def infoMessage(eMessage):
    logMessage(' INFO: ' + eMessage)
    return