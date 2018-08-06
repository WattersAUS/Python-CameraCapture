#!/usr/bin/python3
#
#  Module: picapture.py - G.J. Watson
#    Desc: take vid / pics via pi config.camera when pir sensor is triggered
# Version: 1.00
#

import os
import sys
import time
import getopt
import smtplib
import base64
from email                import encoders
from email.message        import Message
from email.mime.audio     import MIMEAudio
from email.mime.base      import MIMEBase
from email.mime.image     import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from picamera             import PiCamera
from gpiozero import MotionSensor

#our package code
from lib import config
from lib import general

def allowedProgramOptions():
    print('\nusage: picapture.py -c <config file> -v -h\n')
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
We'll send an email with the attached image and video
'''
def sendEmailMessageWithMedia(imageName, movieName, dateString):
    #message setup
    msg            = MIMEMultipart('alternative')
    msg['Subject'] = 'Security message - ' + dateString
    msg['From']    = config.emailFrom
    msg['To']      = config.emailTo

    msg.attach(MIMEText('Motion has been detected by the security config.camera, the image taken has been attached to this email...','plain'))
    msg.attach(MIMEImage(open(imageName, 'rb').read(), name=os.path.basename(imageName)))
    part = MIMEBase('application', 'octet-stream')
    fo   = open(movieName,'rb')
    part.set_payload(fo.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(movieName))
    msg.attach(part)

    #send it!
    try:
        general.logMessage('Preparing to email results to ' + config.emailTo)
        s = smtplib.SMTP(config.emailServer, 587)
        s.starttls()
        s.login(config.emailUser, config.emailPassword)
        s.sendmail(config.emailFrom, config.emailTo, msg.as_string())
        s.quit()
        general.logMessage('Email delivered successfully')
    except smtplib.SMTPRecipientsRefused:
        errMessage('Email delivery failed, invalid recipient')
    except smtplib.SMTPAuthenticationError:
        errMessage('Email delivery failed, authorization error')
    except smtplib.SMTPSenderRefused:
        errMessage('Email delivery failed, invalid sender')
    except smtplib.SMTPException as e:
        errMessage('Email delivery failed, ' + format(e))
    return

'''
First we'll capture an image then immediately followed by a 10 sec vid
'''
def motionDetected():
    general.logMessage('Motion detected, capturing camera image')
    dateString = general.getFormattedCurrentDateTime()
    imageName  = dateString + '.jpg'
    movieName  = dateString + '.h264'
    config.camera.capture(imageName)
    general.logMessage('Now recording video for ' + str(config.videoDuration) + ' seconds')
    config.camera.start_preview()
    config.camera.start_recording(movieName)
    time.sleep(config.videoDuration)
    config.camera.stop_recording()
    config.camera.stop_preview()
    sendEmailMessageWithMedia(imageName, movieName, dateString)
    return

'''
Setup the motion detection and config.camera, then wait!
'''
def startCapture():
    general.logMessage('Initialising motion sensor and picamera')
    config.PIR_PIN = 23
    try:
        config.camera = PiCamera()
        pir = MotionSensor(config.PIR_PIN)
        while True:
            general.logMessage('Waiting for motion for up to ' + str(config.detectionPause) + ' seconds')
            pir.wait_for_motion(config.detectionPause)
            if pir.is_active == True:
                motionDetected()
    except KeyboardInterrupt:
        general.logMessage('Shutting down picamera')
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
