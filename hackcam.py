#!/usr/bin/python

import cv
import paramiko 
import os
import sys

from paramiko import SSHException
from paramiko import Transport
from paramiko import RSAKey 
from paramiko import SFTPClient
from datetime import datetime
from ConfigParser import ConfigParser

CONFIG_FILE = os.getcwd()+"/config"

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

def get_hostkeytype_and_hostkey(host_keys, hostname):
    hostkeytype =  host_keys[hostname].keys()[0]
    hostkey = host_keys[hostname][hostkeytype]

    return hostkeytype, hostkey

def get_privatekey_from_file(pkeyfile, pkeypassword):
    expandedpath = os.path.expanduser(pkeyfile)
    return RSAKey.from_private_key_file(expandedpath, password=pkeypassword)

def sftp_connect(config):
    try:
        hostname = config["hostname"]
        port = int(config["port"])
        username = config["username"]
        pkeyfile = config["privatekey_file"]
        pkeypassword = config["privatekey_passphrase"]

        t = Transport((hostname, port))
        pkey = get_privatekey_from_file(pkeyfile, pkeypassword) 
        t.connect(username=username, pkey=pkey, hostkey=hostkey)

        return SFTPClient.from_transport(t)

    except SSHException, e:
        print " [*] " + str(e)
        sys.exit(1)

def sftp_put(sftp, localpath, remotepath):
    try:
        sftp.put(localpath, "./test.jpg")
    except IOError, e:
        print " [*] " + str(e)
        sys.exit(1)

def parse_configuration():
    config = ConfigParser()
    config.read(CONFIG_FILE)
    config_dict = {}

    for section in config.sections():
        options = config.options(section)

        for option in options:
            try:
                config_dict[option] = config.get(section, option)
            except ConfigParser.Error, e:
                print " [*] " + str(e)
                sys.exit(1)

    return config_dict

if __name__ == "__main__":
    config = parse_configuration()

    camera = cv.CaptureFromCAM(int(config["camera_index"]))
    frame = capture_frame(camera)
    framefilename = datetime.now().strftime("%Y.%m.%d-%H:%M")+".jpg"
    framepath = os.getcwd()+"/"+framefilename

    save_frame_to_file(framepath, frame)

    host_keys = load_host_keys(config["hostkeys_file"])
    hostkeytype, hostkey = get_hostkeytype_and_hostkey(host_keys,
                                                       config["hostname"])

    sftp = sftp_connect(config)
    sftp_put(sftp, framepath, framefilename)
    sftp.close()
