#!/usr/bin/python3
#
#  Module: pistopmotion.py - G.J. Watson
#    Desc: take vid / pics via pi config.camera when pir sensor is triggered
# Version: 1.00
#

import os
import sys
import time
import getopt
from picamera             import PiCamera

#our package code
from lib import config
from lib import general

def allowedProgramOptions():
    print('\nusage: pistopmotion.py -c <config file> -v -h\n')
    print('\t-c configuration file name')
    print('\t-v use verbose logging messages')
    print('\t-s show defaults and terminate')
    print('\t-h this message\n')
    return

def loadConfiguration():
    print('configFilename is ' + config.configFilename)
    return

def showCurrentSettings():
    allowedProgramOptions()
    print('Current defaults:\n')
    print('\tloggingFilename is ' + config.loggingFilename)
    print('\t loggingVerbose is ' + str(config.loggingVerbose))
    print('\t    videoPrefix is ' + config.videoPrefix)
    print('\t  videoDuration is ' + str(config.videoDuration))
    print('\t detectionPause is ' + str(config.detectionPause))
    print('\t    imagePrefix is ' + config.imagePrefix)

    print('\t    emailActive is ' + str(config.emailActive))
    print('\t    emailServer is ' + config.emailServer)
    print('\t      emailFrom is ' + config.emailFrom)
    print('\t      emailUser is ' + config.emailUser)
    print('\t  emailPassword is ' + config.emailPassword)
    print('\t        emailTo is ' + config.emailTo + '\n')
    return

'''
Setup the motion detection and config.camera, then wait!
'''
def startCapture():
    try:
        config.camera = PiCamera()
        while True:
            dateString = general.getFormattedCurrentDateTime()
            general.logMessage('Taking a picture at: ' + dateString)
            imageName  = dateString + '.jpg'
            config.camera.capture(imageName)
            time.sleep(5)
    except KeyboardInterrupt:
        general.logMessage('Shutting down pistopmotion')
        sys.exit()
    return

'''
Check cmd line args set defaults and then pass control to main capture routine
'''
def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hvsc:",["configFilename="])
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                allowedProgramOptions()
                sys.exit()
            elif opt in ('-c', '--configfile'):
                config.configFilename = arg
            elif opt in ('-s', '--show'):
                config.showDefaults = True
            elif opt in ('-v', '--verbose'):
                logLevel = True

        loadConfiguration()
        if config.showDefaults == True:
            showCurrentSettings()
        else:
            startCapture()
    except getopt.GetoptError:
        allowedProgramOptions()
        sys.exit(2)
    return

if __name__ == "__main__":
    main(sys.argv[1:])
