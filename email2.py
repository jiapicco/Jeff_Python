import socket
import ssl, re, os, sys
from imapclient import IMAPClient
from getpass import getpass
import imaplib, threading, queue, time
from newclasses import *
import _thread as thread

"""
Constants
"""
fields=['from', 'bcc', 'body', 'subject', 'cc', 'deleted', 'header', 'sentsince', 'sentbefore', 'senton']
cmds = ['copy', 'move', 'delete', 'fetch']
USERNAME='jai1@prodigy.net'
HOST = 'imap.mail.yahoo.com'
CAFILE = "c:\\strawberry\\perl\\vendor\\lib\\Mozilla\\CA\\cacert.pem"
services=[('Prodigy', HOST, USERNAME),
          ('Exchange','trout.indexengines.com', 'jiapicco'),
          ('Google', 'imap.gmail.com', 'jiapicco@gmail.com')]

mutex = thread.allocate_lock()
mainwin(services, fields, cmds)
