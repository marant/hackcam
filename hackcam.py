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


def capture_frame(camera):
    frame = cv.QueryFrame(camera)
    return frame

def save_frame_to_file(frame, framefile):
    cv.SaveImage(frame, framefile)

def load_host_keys(path):
    try:
        host_keys = paramiko.util.load_host_keys(os.path.expanduser(path))
        return host_keys
    except IOError, e:
        print " [*] " + str(e)
        sys.exit(1)

def get_hostkeytype_and_hostkey(host_keys):
    hostkeytype =  host_keys[HOSTNAME].keys()[0]
    hostkey = host_keys[HOSTNAME][hostkeytype]

    return hostkeytype, hostkey

def get_privatekey_from_file(pkeyfile, pkeypassword):
    expandedpath = os.path.expanduser(pkeyfile)
    return RSAKey.from_private_key_file(expandedpath, password=PKEYPASSWORD)

def sftp_connect(hostkey, hostname, port, username, pkeyfile):
    try:
        t = Transport((HOSTNAME, PORT))
        pkey = get_privatekey_from_file(PKEYFILE, PKEYPASSWORD) 
        t.connect(username=username, pkey=pkey, hostkey=hostkey)

        return SFTPClient.from_transport(t)

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

if __name__ == "__main__":
    camera = cv.CaptureFromCAM(CAMERA_INDEX)
    frame = capture_frame(camera)
    save_frame_to_file("test.jpg", frame)

    host_keys = load_host_keys(HOSTKEYS)
    hostkeytype, hostkey = get_hostkeytype_and_hostkey(host_keys)

    sftp = sftp_connect(hostkey, HOSTNAME, PORT, USERNAME, PKEYFILE)
    sftp_put(sftp, os.getcwd()+"/test.jpg", "test.jpg")
    sftp.close()
