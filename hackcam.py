#!/usr/bin/python

import cv
import paramiko 
import os
import sys

from paramiko import SSHException
from paramiko import Transport
from paramiko import RSAKey 
from paramiko import SFTPClient

CAMERA_INDEX = 0
HOSTKEYS = "~/.ssh/known_hosts"
HOSTNAME = "192.168.100.40"
PORT = 22
USERNAME = "user"
PKEYFILE = "/home/marant/.ssh/id_rsa"
PKEYPASSWORD = ""

camera = cv.CaptureFromCAM(CAMERA_INDEX)

def captureFrame(camera):
    frame = cv.QueryFrame(camera)
    return frame

def saveFrameToFile(frame, framefile):
    cv.SaveImage(frame, framefile)

def loadHostKeys(path):
    try:
        host_keys = paramiko.util.load_host_keys(os.path.expanduser(path))
        return host_keys
    except IOError, e:
        print " [*] " + str(e)
        sys.exit(1)

def getHostKeyAndKeyType(host_keys):
    hostkeytype =  host_keys[HOSTNAME].keys()[0]
    hostkey = host_keys[HOSTNAME][hostkeytype]

    return hostkeytype, hostkey

def getPrivateKeyFromFile(pkeyfile, pkeypassword):
    return RSAKey.from_private_key_file(pkeyfile) 

def connect(hostkey, hostname, port, username, pkeyfile):
    try:
        t = Transport((HOSTNAME, PORT))
        pkey = getPrivateKeyFromFile(PKEYFILE, PKEYPASSWORD) 
        t.connect(username=username, pkey=pkey, hostkey=hostkey)
        return t
    except SSHException, e:
        print " [*] " + str(e)
        sys.exit(1)

def initializeSFTPClient(transport):
    return SFTPClient.from_transport(transport)

def sftp_put(sftp, localpath, remotepath):
    try:
        sftp.put(localpath, "./test.jpg")
    except IOError, e:
        print " [*] " + str(e)
        sys.exit(1)

    

frame = captureFrame(camera)
saveFrameToFile("test.jpg", frame)

host_keys = loadHostKeys(HOSTKEYS)
hostkeytype, hostkey = getHostKeyAndKeyType(host_keys)
transport = connect(hostkey, HOSTNAME, PORT, USERNAME, PKEYFILE )

sftp = initializeSFTPClient(transport)
sftp_put(sftp, os.getcwd()+"/test.jpg", "test.jpg")
sftp.close()


