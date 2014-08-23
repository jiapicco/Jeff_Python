import socket
import ssl, re, os, sys
from imapclient import IMAPClient
from getpass import getpass
import imaplib
from newclasses import *

"""
Constants
"""
fields=['from', 'bcc', 'body', 'subject', 'cc', 'deleted', 'header', 'sentsince', 'sentbefore', 'senton']
cmds = ['copy', 'move', 'delete', 'fetch']
USERNAME='jai1@prodigy.net'
HOST = 'imap.mail.yahoo.com'
CAFILE = "c:\\strawberry\\perl\\vendor\\lib\\Mozilla\\CA\\cacert.pem"
services=[('Prodigy', HOST, USERNAME), ('Exchange', 'trout.indexengines.com', 'jiapicco')]

mainwin(services, fields, cmds)
