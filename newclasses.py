import socket
import ssl, re, os, sys
from imapclient import IMAPClient
from getpass import getpass
import imaplib
from tkinter import *
from tkinter.messagebox import *
import threading, queue, time
global print_mutex
import _thread as thread

"""
Will make changes for multi-threading
"""

"""
Mail client class
"""
class mail_client(imaplib.IMAP4_SSL):
  global print_mutex
  def __init__(self, HOST, PORT=993, KEYFILE=None, CAFILE=None):
    imaplib.IMAP4_SSL.__init__(self, host=HOST, port=PORT, keyfile=KEYFILE, certfile=CAFILE)

  def prnt(self):
    global print_mutex
    with print_mutex: print("in new method")

  def login(self, USERNAME, PASSWORD):
    global print_mutex
    #Connect to the mail server and log in
    try:
      imaplib.IMAP4_SSL.login(self, USERNAME, PASSWORD)
    except Exception as e:
      with print_mutex: print(e)
      return(False)
    else:
      return(True)

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
    #Super class must provide __init__
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

  def __init__(self, inputs, fields, cmds, mutex, mqueue):
    global print_mutex
    
    self.top = Tk()
    self.top.geometry('{}x{}'.format(500, 200))
    self.top.title('Select Mail Service')
    for inpt in inputs:
      btn(self.top, inpt[0], inpt[1], inpt[2], fields, cmds, mutex, mqueue)
    but = Button(self.top, text='Quit', command = (lambda: self.gui_quit(self.top)))
    but.pack(side=LEFT)
    chk_but = Button(self.top, text = 'Check', command = (lambda: self.check_queue(mqueue))).pack(side=RIGHT)
    self.top.bind('RETURN', (lambda: self.check_queue(mqueue)))
    self.mqueue = mqueue
    self.check_queue()
    self.top.mainloop()

  def check_queue(self):
    try:
      (callback, args) = self.mqueue.get(block=False)
    except queue.Empty:
      pass
    else:
      print('%s, %s' % (callback, args))
      callback(args)
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
  def start_service(self, host, username, fields, cmds, mutex, mqueue):
    mail = mail_client(host)
    req_pw(mail, username, fields, cmds, mutex, mqueue)


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
  def __init__(self, mail, USERNAME, fields, cmds, mutex, mqueue):
    self.mutex = mutex
    top = Tk()
    top.geometry('{}x{}'.format(500, 200))
    top.title('Login')
    Label(top, text='Enter Password').pack(side=TOP)
    ent = Entry(top, show="*")
    ent.pack(side=TOP, expand=YES)
    btn = Button(top, text='Submit', command = (lambda: self.login(mail, USERNAME, ent.get(), top, fields, cmds, mqueue)))
    btn.pack(side=LEFT)
    top.bind('<Return>', (lambda event: self.login(mail, USERNAME, ent.get(), top, fields, cmds, mqueue)))
    Button(top, text='Quit', command = (lambda: self.gui_quit(top))).pack(side=RIGHT)
    #top.mainloop()
    return
  def login(self, mail, USERNAME, PASSWORD, top, fields, cmds, mqueue):
    global print_mutex
    if((mail.login(USERNAME, PASSWORD)) == True):
      top.destroy()
      boxes = mail.get_boxes()
      top = req_query(boxes, fields, cmds, mail, self.mutex, mqueue)
    else:
      top.destroy()
      req_pw(mail, USERNAME, fields, cmds)

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
    #top.mainloop()
    return
  def response(self, top, ent):
    self.respnse = ent
    print('destroying req_input')
    self.done = True
    top.destroy()
    return 
  def get_val(self):
    if(self.done == False):
      return (False, '')
    else:
      return (True, self.respnse)

"""
Class for a GUI window that provides status information to the user
"""
class status(MyGui):
  def __init__(self, txt):
    top = Tk()
    top.geometry('{}x{}'.format(500, 200))
    top.title(txt)
    btn = Button(top, text='Dismiss', command = (lambda: self.dismiss(top)))
    top.bind('<Return>', (lambda event: self.dismiss(top)))
    btn.pack(side=BOTTOM)
    return 

"""
Class for the thread that will perform the actual search
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
    global print_mutex
    lst = []
    try:
      self.mail.select(self.mailbox)
    except Exception as e:
      with self.mutex: print(e)
      self.queue.put((False, lst))
    else:
      try:
        typ, lst = self.mail.search(None, '%s' % self.query)
      except Exception as e:
        with self.mutex: print('mailbox = %s, exception = %s' % (self.mailbox,e))
        self.queue.put((False, lst))
      else:
        lst=lst[0].decode('utf-8')
        lst=lst.split( )
        self.queue.put((True, lst))
    
"""
Class for the thread that will perform email copy
"""
class email_copy(threading.Thread):
  def __init__(self,  mail, msg, mailbox, queue, mutex):
    global print_mutex
    threading.Thread.__init__(self)
    self.mail = mail
    self.msg = msg
    self.mailbox = mailbox
    self.queue = queue
    self.mutrex = mutex

  def run(self):
    for a in self.msg:
      try:
        self.mail.copy(a, self.mailbox)
      except Exception as e:
        with self.mutex: print('in email_copy, e = %s' % e)
        self.queue.put(False)
        return

    self.queue.put(True)

"""
Class for the thread that moves messages
"""
class email_move(threading.Thread):
  global print_mutex
  def __init__(self, mail, msg, d_box, queue, mutex):
    threading.Thread.__init__(self)
    elf.mail = mail
    self.msg = msg
    self.d_box = d_box
    self.queue = queue
    self.mutex = mutex

  def run(self):
    success = 1
    failed = 0
    for a in self.msg:
      try:
        self.mail.copy(a, self.d_box)
      except Exception as e:
        with self.mutex: print(e)
        success = 0
    #Only delete if copy succeeded
    if(success == 1):
      for a in lst:
          try:
            typ, response = self.mail.store(a,  '+FLAGS', r'(\Deleted)')
          except Exception as e:
            with print_mutex: print(e)
      self.queue.put(True, failed)
      return 
    else:
      self.queue.put(False, failed)
      return
          

"""
Class for GUI window that collects information for the query and then calls the
method that is the main processing loop when the user submits input.
"""
class req_query(MyGui):
  def __init__(self, boxlst, fields, cmds, mail, mutex, mqueue):
    self.mutex = mutex
    top = Tk()
    top.geometry('{}x{}'.format(500, 600))
    top.title('Enter Query')
    ents, s_menu, a_menu = self.make_query(top, fields, boxlst, cmds)
    top.bind('<Return>', (lambda event: self.fetch(ents, s_menu, a_menu, top, boxlst, fields, mail, mutex, mqueue)))
    Button(top, text='Submit', command = (lambda: self.fetch(ents, s_menu, a_menu, top, boxlst, fields, mail, mutex, mqueue))).pack(side=LEFT)
    Button(top, text='Quit', command = (lambda: self.gui_quit(top, mail))).pack(side=RIGHT)
    #top.mainloop()
    return

  def gui_quit(self, top, mail):
    try:
      mail.close()
    except Exception as e:
      with self.mutex: print(e)
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
      Radiobutton(c_lst, text = txt, variable = self.var, value = txt, command = (lambda: self.on_press())).pack(anchor=W)
      self.var.set(txt)
    c_lst.pack(side = TOP, fill = X)
    a_box = Frame(top)
    a_menu = ScrolledList(boxlst, a_box, 6, 'Destination Mailbpox', 15)
    a_box.pack(side=TOP, fill=X)
    self.name = status_frame(top)
    return entries, s_menu, a_menu

  def on_press(self):
    #print('radio button %s selected' % self.var.get())
    pass
  
  def fetch(self, ents, s_menu, a_menu, top, boxes, fields, mail, mutex, mqueue):
    print('in fetch')
    s_box = s_menu.get_val()
    cmd = self.var.get()
    a_box = a_menu.get_val() 
    query = {}
    i = 0
    for entry in ents:
      query[fields[i]] = entry.get()
      i += 1
    #self.loop(s_box, query, cmd, a_box, boxes, mail)
      """
    if(cmd == 'delete'):
      x = req_input('Do youy really want to delete messages from %s?' % s_box)
      while(True):
        time.sleep(2)
        tst, res = x.get_val()
        print(tst)
        if(tst == True): break
      print(res)
      if(res == 'y' or res == 'Y'):
        print('doing delete')
        thread.start_new_thread(loop, (s_box, query, cmd, a_box, boxes, mail, mutex, mqueue))
    else:
      thread.start_new_thread(loop, (s_box, query, cmd, a_box, boxes, mail, mutex, mqueue))
      """
    thread.start_new_thread(loop, (s_box, query, cmd, a_box, boxes, mail, mutex, mqueue, self.name))
    return

class status_frame():
  def __init__(self, top):
    self.row = Frame(top)
    self.var = StringVar(self.row)
    self.var.set('Status: ')
    self.lab = Label(self.row, textvariable = self.var).pack(side=TOP)
    self.row.pack(fill=X)

  def update(self, txt):
    print('Running status_update')
    self.var.set('Status: '+txt)
  

def loop(mailbox, query, cmd, a_box, boxlst, mail, print_mutex, mqueue, name):
  dqueue = queue.Queue()
  mqueue.put((name.update, 'Running query.'))
  with print_mutex: print('in loop')
  #Prepare the query by adding individual terms
  search_query = '('
  for key in query.keys():
    if query[key]:
      if (len(search_query) > 1):
        search_query = search_query+' '
      search_query = search_query+'%s \"%s\"' % (key, query[key])
  search_query = search_query+')'
  #print('Query = %s' % search_query)
  if (mailbox != 'ALL'):
    t = email_search(mail, search_query, mailbox, dqueue, print_mutex)
    t.start()
    while(True):
      time.sleep(3)
      try:
        (result, lst) = dqueue.get(block=False)
      except queue.Empty:
        pass
      else:
        break

  else:
    i = 0
    box = a_box
    for mailbox in (boxlst):
      if(box == mailbox or mailbox == 'ALL'): continue
      t = email_search(mail, search_query, mailbox, dqueue, print_mutex)
      t.start()
      while(True):
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
    #status('No messages that matched query.')
    mqueue.put((status, ('No messages that matched query.')))
    with print_mutex: print('No messages that matched query.')
    return
  
  else:
    
    ans = cmd
    #Delete
    if ans == 'delete':
      #res = req_input('%i Messages found, do you really want to delete these messages? (y/n)' % len(lst))
      #ans = res.get_val()
      with print_mutex: ans = input('%i Messages found, do you really want to delete these messages? (y/n): ' % len(lst))
      if(ans == 'y' or ans == 'Y'):
        for a in lst:
          try:
            typ, response = mail.store(a,  '+FLAGS', r'(\Deleted)')
          except Exception as e:
            with print_mutex: print(e)
        mqueue.put((name.update, ('%i Messages deleted.' % len(lst))))
      return len(lst)

    #Move - actually copy and delete
    elif ans == 'move':
      #status('%i Messages found.' % len(lst))
      mqueue.put((name.update, ('%i Messages found.' % len(lst))))
      with print_mutex: print('%i Messages found.' % len(lst))
      box = a_box
      t = email_move(mail, lst, a_box, dqueue)
      t.start
      while(True):
        time.sleep(3)
        try:
          result, failed = dqueue.get(block=False)
        except queue.Empty:
          pass
        else:
          break
      if(result == False):
        #status('%i Messaged failed copy during move.' % failed)
        with print_mutex: print('%i Messaged failed copy during move.' % failed)


    #Copy
    elif ans == 'copy':
      #status('%i Messages found. Copied to %s' % (len(lst), a_box))
      mqueue.put((name.update, ('%i Messages found. Copied to %s' % (len(lst), a_box))))
      with print_mutex: print('%i Messages found. Copied to %s' % (len(lst), a_box))
      t = email_copy(mail, lst, a_box, dqueue, print_mutex)
      t.start()
      while(True):
        time.sleep(3)
        try:
          resukt = dqueue.get(block=False)
        except queue.Empty:
          pass
        else:
          break
      return len(lst)

    #Fetch message
    elif ans == 'fetch':
      #status('%i Messages found.' % len(lst))
      mqueue.put((name.update, ('%i Messages found.' % len(lst))))
      with print_mutex: print('%i Messages found.' % len(lst))
      for a in lst:
        try:
          typ, data = mail.fetch(a, '(BODY.PEEK[TEXT])')
        except Exception as e:
          with print_mutex: print (e)
        with print_mutex: print(data)
      return len(lst)
        
