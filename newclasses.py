import socket
import ssl, re, os, sys
from imapclient import IMAPClient
from getpass import getpass
import imaplib, email, pdb
from tkinter import *
from tkinter.messagebox import *
import threading, queue, time
global print_mutex
import _thread as thread

"""
Constants
"""

#Fields in the email that can be searched
fields=['from', 'bcc', 'body', 'subject', 'cc', 'deleted', 'header', 'sentsince', 'sentbefore', 'senton']

#Commands the user can execute
cmds = ['copy', 'move', 'delete', 'fetch']

#SSL Certificate File
CAFILE = "c:\\strawberry\\perl\\vendor\\lib\\Mozilla\\CA\\cacert.pem"


#Email services
services=[('Prodigy', 'imap.mail.yahoo.com', 'jai1@prodigy.net'),
          ('Exchange','trout.indexengines.com', 'jiapicco'),
          ('Google', 'imap.gmail.com', 'jiapicco@gmail.com')]



"""
Create global message queue (mqueue) and mutex for printing (print_mutex)
"""
mqueue = queue.Queue()
print_mutex = thread.allocate_lock()

"""
function to display erroros
"""
def log(service, txt):
  global mqueue, print_mutex
  mqueue.put((status, (service, txt)))
  with print_mutex: print('%s: %s' % (service, txt))
  return


"""
Mail client class
"""
class mail_client(imaplib.IMAP4_SSL):

  def __init__(self, sname, mutex, HOST, PORT=993, KEYFILE=None, CAFILE=None):
    imaplib.IMAP4_SSL.__init__(self, host=HOST, port=PORT, keyfile=KEYFILE, certfile=CAFILE)
    self.print_mutex = mutex
    self.name = sname
  def prnt(self):
    global print_mutex
    #log("in new method")
    log("in new method")

  def login(self, USERNAME, PASSWORD):
    #Connect to the mail server and log in
    try:
      imaplib.IMAP4_SSL.login(self, USERNAME, PASSWORD)
    except Exception as e:
      log(self.name, e)
      return(False)
    else:
      return(True)


    
  """
  This method returns the name of the service for the imap session.
  """
  def get_name(self):
    return self.name

  """
  Gets a list of all of the mailboxes
  """
  def get_boxes(self):
    typ, boxes=self.list()
    boxlst=[]
    for term in (boxes):
      term=term.decode('utf-8') 
      match = re.match('(?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)', term)
      mailbox=match.group(3)
      boxlst.append(mailbox)
    boxlst.sort(key=str.lower)
    return boxlst

"""
Sub-class for GUI windows
"""
class MyGui(Frame):
  def __init__(self, parent=None):
    #Sub-class must provide __init__
    pass
  def gui_quit(self, top):
    top.destroy()
    sys.exit()
  def dismiss(self, top):
    top.destroy()
    return

"""
Class for the main GUI window
"""
class mainwin(MyGui):

  def __init__(self, inputs, fields, cmds):
    global print_mutex, mqueue
    mutex = print_mutex
    self.top = Tk()
    self.top.geometry('{}x{}'.format(500, 200))
    self.top.title('Select Mail Service')
    for inpt in inputs:
      btn(self.top, inpt[0], inpt[1], inpt[2], fields, cmds, mutex, mqueue)
    but = Button(self.top, text='Quit', command = (lambda: self.gui_quit(self.top)))
    but.pack(side=LEFT)
    chk_but = Button(self.top, text = 'Check', command = (lambda: self.check_queue(mqueue))).pack(side=RIGHT)
    self.top.bind('RETURN', (lambda: self.check_queue()))
    self.mqueue = mqueue
    self.check_queue()
    self.top.mainloop()

  """
  This  method periodically checks the queue for the threads and runs the call back
  function with the returned arguments (args)
  Check for up to three (3) items on the queue
  """
  def check_queue(self):
    global mqueue
    i = 0
    while(i <= 3):
      try:
        (callback, args) = self.mqueue.get(block=False)
      except queue.Empty:
        break
      else:
        callback(args)
      i += 1
    self.top.after(1000, self.check_queue)

    
"""
Class for button that can take action
"""
class btn():
  def __init__(self, top, label, host, username, fields, cmds, mutex, mqueue):
    row = Frame(top)
    but = Button(row, text=label, command = (lambda: self.start_service(host, username, fields, cmds, mutex, mqueue)))
    but.pack()
    row.pack()
    self.name = label
    self.mutex = mutex
  def start_service(self, host, username, fields, cmds, mutex, mqueue):
    #mail = mail_client(self.name, mutex, host, 993, None, CAFILE)
    mail = mail_client(self.name, mutex, host)
    req_pw(mail, username, fields, cmds, mutex)


"""
Class for a list box with a scroll bar
"""
class ScrolledList(Frame):
  def __init__(self, options, parent=None, height=7, title='', width=15):
    Frame.__init__(self, parent)
    self.pack(expand=YES, fill=BOTH)
    self.makeWidgets(options, height, width, title)

  def handleList(self, event):
    index = self.listbox.curselection()
    label = self.listbox.get(index)
    self.runCommand(label)

  def makeWidgets(self, options, in_height, in_width, title):
    stit = Frame(self)
    lab = Label(stit, width = in_width, text = title)
    lab.pack(side=LEFT)
    stit.pack()
    sbar = Scrollbar(self)
    lst = Listbox(self, relief=SUNKEN, height=in_height)
    sbar.config(command=lst.yview)
    sbar.pack(side=RIGHT, fill=Y)
    lst.pack(side=LEFT, expand=YES, fill=BOTH)
    pos = 0
    for label in options:
      lst.insert(pos, label)
      pos += 1
    #lst.config(selectmode=SINGLE, setgrid=1)
    lst.bind('<Double-1>', self.handleList)
    self.listbox = lst

  def runCommand(self, selection):
    self.respnse = selection

  def get_respnse(self):
    return self.respnse

  def get_val(self):
    val = self.listbox.get(ACTIVE)
    return val

"""
Class for a GUI window that asks for password and completes login process
"""
class req_pw(MyGui):
  def __init__(self, mail, USERNAME, fields, cmds, mutex):
    global mqueue
    self.mutex = mutex
    top = Tk()
    top.geometry('{}x{}'.format(500, 200))
    top.title('Login')
    Label(top, text='Enter Password for %s' % mail.get_name()).pack(side=TOP)
    ent = Entry(top, show="*")
    ent.pack(side=TOP, expand=YES)
    btn = Button(top, text='Submit', command = (lambda: self.login(mail, USERNAME, ent.get(), top, fields, cmds)))
    btn.pack(side=LEFT)
    top.bind('<Return>', (lambda event: self.login(mail, USERNAME, ent.get(), top, fields, cmds)))
    Button(top, text='Quit', command = (lambda: self.gui_quit(top))).pack(side=RIGHT)
    return
  def login(self, mail, USERNAME, PASSWORD, top, fields, cmds):
    global print_mutex, mqueue
    if((mail.login(USERNAME, PASSWORD)) == True):
      top.destroy()
      boxes = mail.get_boxes()
      top = req_query(boxes, fields, cmds, mail, self.mutex, mqueue)
    else:
      top.destroy()
      req_pw(mail, USERNAME, fields, cmds, self.mutex)

"""
Class for a GUI window that prompts the user to provide tyext inpout
"""
class req_input(MyGui):
  def __init__(self, txt):
    self.done = False
    top = Tk()
    top.geometry('{}x{}'.format(500, 200))
    top.title(txt)
    ent = Entry(top)
    ent.config(width=400)
    ent.pack(side=TOP)
    btn = Button(top, text='Submit', command = (lambda: self.response(top, ent.get())))
    top.bind('<Return>', (lambda event: self.response(top, ent.get())))
    btn.pack(side=LEFT)
    Button(top, text='Quit', command = (lambda: self.gui_quit(top))).pack(side=RIGHT)
    return
  def response(self, top, ent):
    self.respnse = ent
    self.done = True
    top.destroy()
    return 
  def get_val(self):
    if(self.done == False):
      return (False, '')
    else:
      return (True, self.respnse)

"""
This GUI class is used to confirm that operations should take place.
This method will be called as a callable via check_queue. The arguments are:
   - Name of the service, will be used in the title of dialog box
   - Text to be displayed to the user
   - Callable to be used if the user selects continue
   - Arguments for the callable

These argumnents are contained in a tuple that must be converted to a list for processing.
"""
class confirm(MyGui):
  def __init__(self, args):
    args_list = list(args)
    top = Tk()
    top.title(args_list[0])
    top.geometry('{}x{}'.format(500, 200))
    row = Frame(top)
    Label(row, text = args_list[1]).pack(side=TOP)
    row.pack(fill=X)
    btn = Button(top, text='Continue', command = (lambda: self.proceed(top, (args_list[2:]))))
    top.bind('<Return>', (lambda event: self.proceed(top, (args_list[2:]))))
    btn.pack(side=LEFT)
    Button(top, text='Cancel', command = (lambda: self.dismiss(top))).pack(side=RIGHT)
    return

  """
  The first item in args is the function to be called and the remaining items
  the argument to be passed the function
  """
  def proceed(self, top, args):
    top.destroy()
    func = args[0]
    #convert args to tuple for passing to func
    thread.start_new_thread(func, (tuple(args[1:])))
    return

"""
Class for a GUI window that provides status information to the user
"""
class status(MyGui):
  def __init__(self, args):
    service = args[0]
    txt = args[1]
    top = Tk()
    top.title(service)
    top.geometry('{}x{}'.format(700, 200))
    Label(top, text = txt).pack(side=TOP)
    btn = Button(top, text='Dismiss', command = (lambda: self.dismiss(top)))
    top.bind('<Return>', (lambda event: self.dismiss(top)))
    btn.pack(side=BOTTOM)
    return 

"""
Class for the thread that will perform the actual search, uses the
threading object model for threads
"""
class email_search(threading.Thread):
  def __init__(self,  mail, query, mailbox, queue, mutex):
    global print_mutex
    threading.Thread.__init__(self)
    self.mail = mail
    self.query = query
    self.mailbox = mailbox
    self.queue = queue
    self.mutex = mutex
    

  def run(self):
    lst = []
    try:
      self.mail.select(self.mailbox)
    except Exception as e:
      log(self.mail.get_name(), e)
      self.queue.put((False, lst))
      return
    else:
      try:
        typ, lst = self.mail.search(None, '%s' % self.query)
      except Exception as e:
        log('mailbox = %s, exception = %s' % (self.mailbox,e))
        self.queue.put((False, lst))
      else:
        lst=lst[0].decode('utf-8')
        lst=lst.split( )
        self.queue.put((True, lst))
        return
    
"""
Class for the thread that will perform email copy, uses the
threading object model for threads
"""
class email_copy(threading.Thread):
  def __init__(self,  mail, msg, mailbox, queue, mutex):
    global print_mutex
    threading.Thread.__init__(self)
    self.mail = mail
    self.msg = msg
    self.mailbox = mailbox
    self.queue = queue
    self.mutex = mutex

  def run(self):
    for a in self.msg:
      try:
        self.mail.copy(a, self.mailbox)
      except Exception as e:
        log(self.mail.get_name(), 'in email_copy, e = %s' % e)
        self.queue.put(False)
        return

    self.queue.put(True)

"""
Class for the thread that moves messages, uses the
threading object model for threads
"""
class email_move(threading.Thread):
  global print_mutex
  def __init__(self, mail, msg, s_box, d_box, queue, mutex):
    threading.Thread.__init__(self)
    self.mail = mail
    self.msg = msg
    self.s_box = s_box
    self.d_box = d_box
    self.queue = queue
    self.mutex = mutex

  def run(self):
    success = 1
    failed = 0
    new_list = self.msg
    i = 0
    try:
      self.mail.select(self.s_box)
    except Exception as e:
      log(self.mail.get_name(), e)
      self.queue.put(False)
      return
    for a in self.msg:
      try:
        self.mail.copy(a, self.d_box)
      except Exception as e:
        log(self.mail.get_name(), e)
        success = 0
    #Only delete if copy succeeded
    if(success == 1):
      for a in new_list:
        try:
          typ, response = self.mail.store(a,  '+FLAGS', r'(\Deleted)')
        except Exception as e:
          log(self.mail.get_name(), e)
      self.queue.put(True)
      return 
    else:
      self.queue.put(False)
      return
          

"""
Class for GUI window that collects information for the query and then calls the
function (run_query) that is the main processing thread when the user submits input.
"""
class req_query(MyGui):
  def __init__(self, boxlst, fields, cmds, mail, mutex, mqueue):
    self.mutex = mutex
    self.mail = mail
    top = Tk()
    top.geometry('{}x{}'.format(500, 700))
    top.title(mail.get_name())
    ents, s_menu, self.a_menu = self.make_query(top, fields, boxlst, cmds)
    top.bind('<Return>', (lambda event: self.fetch(ents, s_menu, self.a_menu, top, boxlst, fields, mail, mutex, mqueue)))
    Button(top, text='Submit', command = (lambda: self.fetch(ents, s_menu, self.a_menu, top, boxlst, fields, mail, mutex, mqueue))).pack(side=LEFT)
    Button(top, text='Quit', command = (lambda: self.gui_quit(top, mail))).pack(side=RIGHT)
    #top.mainloop()
    return

  def gui_quit(self, top, mail):
    try:
      mail.logout()
    except Exception as e:
      log(self.mail.get_name(), e)
    top.destroy()
  
  def make_query(self, top, fields, boxlst, cmds):
    entries = []
    s_box = Frame(top)
    q_lst=['ALL', 'inbox']+boxlst
    s_menu = ScrolledList(q_lst, s_box, 6, 'Search Mailbox', 15)
    s_box.pack(side=TOP, fill=X)
    term_box = Frame(top)
    term_box_lab = Label(term_box, width = 15, text='Search Terms')
    term_box_lab.pack(side=LEFT)
    term_box.pack()
    for field in fields:
      row = Frame(top)
      lab = Label(row, width = 15, text = field)
      ent = Entry(row)
      ent.config(width=400) 
      row.pack(side=TOP, fill=X)
      lab.pack(side=LEFT)
      ent.pack(side=RIGHT, expand=YES, fill=X)
      entries.append(ent)
    c_lst = Frame(top)
    c_lst_lab = Label(c_lst, width = 15, text='Actions')
    c_lst_lab.pack(side = LEFT)
    self.var = StringVar(c_lst)
    for txt in cmds:
      Radiobutton(c_lst, text = txt, variable = self.var, value = txt, command = (lambda: self.on_press(top, boxlst))).pack(anchor=W)
      self.var.set(txt)
    c_lst.pack(side = TOP, fill = X)
    #variable to describe if the destination mailbox selection box is visible
    self.make_dest_vis = False
    #create variable used by the destination mailbox selection box
    self.a_box = None
    self.a_menu = None
    """
    Frame object that will be used to update status information. sel.name is a reference to the
    status_frame object.
    """

    self.name = status_frame(top)
    return entries, s_menu, self.a_menu

  """
  This method will make the destination mailbox selection box visible if the copy or move commands are selected.
  The variable self.make_dest_vis is True if the selection box is currently being displayed and is False if
  the selection box is not cutrrently being displayed.
  """
  def on_press(self, top, boxlst):
    print('radio button %s selected' % self.var.get())
    cmd = self.var.get()
    if (cmd == 'copy' or cmd == 'move'):
      if(self.make_dest_vis == False):
        self.make_dest_vis = True
        self.a_box = Frame(top)
        self.a_menu = ScrolledList(boxlst, self.a_box, 6, 'Destination Mailbpox', 15)
        self.a_box.pack(side=TOP, fill=X)
      else:
        return
    elif(self.make_dest_vis == True):
      self.make_dest_vis = False
      self.a_box.destroy()

  
  def fetch(self, ents, s_menu, a_menu, top, boxes, fields, mail, mutex, mqueue):
    s_box = s_menu.get_val()
    cmd = self.var.get()
    #Check to see if destination selection box is visible, if so use that value other wise pass empty string
    if(self.make_dest_vis == True):
      a_box = a_menu.get_val()
    else:
      a_box = ''
    query = {}
    i = 0
    for entry in ents:
      query[fields[i]] = entry.get()
      i += 1
    thread.start_new_thread(run_query, (s_box, query, cmd, a_box, boxes, mail, mutex, mqueue, self.name))
    return

"""
Class for frame in the Query that contains status.  Gets updated by a callback to update() that
includes the string to be displayed.
"""
class status_frame():
  def __init__(self, top):
    self.row = Frame(top)
    self.var = StringVar(self.row)
    self.var.set('Status: ')
    self.lab = Label(self.row, textvariable = self.var).pack(side=TOP)
    self.row.pack(fill=X)

  def update(self, txt):
    self.var.set('Status:\n'+txt)
  
"""
The main thread that executes the query.  If 'move' or 'delete' are selected as the command
to execute a callback to the confoirm class is used to get user confirmation to proceed.
"""
def run_query(mailbox, query, cmd, a_box, boxlst, mail, print_mutex, mqueue, name):
  dqueue = queue.Queue()
  mqueue.put((name.update, 'Running query.'))
  search_query = '('
  for key in query.keys():
    if query[key]:
      if (len(search_query) > 1):
        search_query = search_query+' '
      search_query = search_query+'%s \"%s\"' % (key, query[key])
  search_query = search_query+')'
  if (mailbox != 'ALL'):
    t = email_search(mail, search_query, mailbox, dqueue, print_mutex)
    t.start()
    while(True):
      time.sleep(.5)
      try:
        (result, lst) = dqueue.get(block=False)
      except queue.Empty:
        pass
      else:
        mqueue.put((name.update, 'Query complete.'))
        break

  else:
    i = 0
    box = a_box
    for mailbox in (boxlst):
      if(box == mailbox or mailbox == 'ALL'): continue
      t = email_search(mail, search_query, mailbox, dqueue, print_mutex)
      t.start()
      while(True):
        time.sleep(.5)
        try:
          (result, tmp) = dqueue.get(block=False)
        except queue.Empty:
          pass
        else:
          break
      i += len(tmp)
      if(len(tmp) > 0):
        #mail.copy(a, box)
        t = email_copy(mail, tmp, box, dqueue, print_mutex)
        t.start()
        while(True):
          try:
            result = dqueue.get(block=False)
          except queue.Empty:
            pass
          else:
            break
                       
    mqueue.put((name.update, ('%i Messages found.' % i)))
    return

  #If messages were found ask for what to do, else inform user that not messages matchedthe query
  if(len(lst)==0):
    mqueue.put((name.update, ('No messages that matched query.')))
    return
  
  else:
    
    ans = cmd
    #Delete
    if ans == 'delete':
      mqueue.put((confirm, ((mail.get_name(), '%i Messages found in %s, \ndo you really want to delete these messages?' % (len(lst), mailbox), \
                             delete,  mail, mailbox, lst, print_mutex, mqueue, name))))
      return

    #Move - actually copy and delete
    elif ans == 'move':
      mqueue.put((confirm, ((mail.get_name(), '%i Messages found in %s, \ndo you really want to move these messages?' % (len(lst), mailbox), \
                             move,  mail, mailbox, a_box, lst, print_mutex, dqueue, mqueue, name))))
      return


    #Copy
    elif ans == 'copy':
      mqueue.put((name.update, ('%i Messages found. Copied to %s' % (len(lst), a_box))))
      t = email_copy(mail, lst, a_box, dqueue, print_mutex)
      t.start()
      while(True):
        time.sleep(.5)
        try:
          resukt = dqueue.get(block=False)
        except queue.Empty:
          pass
        else:
          break
      return len(lst)

    #Fetch message
    elif ans == 'fetch':
      mqueue.put((name.update, ('%i Messages found.' % len(lst))))
      log(mail.get_name(), '%i Messages found.' % len(lst))
      for a in lst:
        try:
          #typ, data = mail.fetch(a, '(BODY.PEEK[TEXT])')
          typ, data = mail.fetch(a,'(RFC822)')
          #msg = email.message_from_string(data[0][1])
          
        except Exception as e:
          log (e)
        #log(mail.get_name(), data)
        sdata = str(data[0][1])
        #sdata = sdata[2:]
        #sdata = sdata[:-1]
        msg = email.message_from_string(str(data[0][1]))
        maintype = msg.get_content_maintype()
        if (maintype == 'multipart'):
          with print_mutex: print('Multipart!!!')
          for part in msg.walk():
            if part.get_content_type() == 'text/plain':
              with print_mutex: print(part.get_payload())
        elif (maintype == 'text'):
          with print_mutex: print('Text!!!')
          with print_mutex: print(msg.get_payload())
    return len(lst)

"""
Function to perform deletion of emails. This is called after the user
confirms that the operation should continue.
"""
def delete (mail, box, lst, mutex, mqueue, name):
  mqueue.put((name.update, ('Deleting %i messages.' % len(lst))))
  try:
    mail.select(box)
  except Exception as e:
    log(mail.get_name(), e)
    return
  for a in lst:
    try:
      typ, response = mail.store(a,  '+FLAGS', r'(\Deleted)')
    except Exception as e:
      log(mail.get_name(), e)
    if(typ == False):
      log(mail.get_name(), 'Error in delete')
  mqueue.put((name.update, ('%i Messages deleted.' % len(lst))))

"""
Function to perform move of emails. This is called after the user
confirms that the operation should continue.
"""
def move(mail, mailbox, a_box, lst, print_mutex, dqueue, mqueue, name):
  mqueue.put((name.update, ('Moving %i messages' % len(lst))))
  t = email_move(mail, lst, mailbox, a_box, dqueue, print_mutex)
  t.start()
  while(True):
    try:
      result= dqueue.get(block=False)
    except queue.Empty:
      pass
    else:
      break
  if(result == False):
    log(mail.get_name(), 'Messages failed copy during move.' )
    return
  else:
    mqueue.put((name.update, ('%i Messages moved' % len(lst))))

    
#
#
#______________________________________________________________________________________
#
#


"""
Here is the call to start the main window of the GUI that gets everythoing going
"""

print(CAFILE)
mainwin(services, fields, cmds)

        

