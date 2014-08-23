import socket
import ssl, re, os, sys
from imapclient import IMAPClient
from getpass import getpass
import imaplib
from tkinter import *
from tkinter.messagebox import *

"""
This is just to see a change in nGit
"""


"""
Mail client class
"""
class mail_client(imaplib.IMAP4_SSL):
  def __init__(self, HOST, PORT=993, KEYFILE=None, CAFILE=None):
    imaplib.IMAP4_SSL.__init__(self, host=HOST, port=PORT, keyfile=KEYFILE, certfile=CAFILE)

  def prnt(self):
    print("in new method")

  def login(self, USERNAME, PASSWORD):
    #Connect to the mail server and log in
    try:
      imaplib.IMAP4_SSL.login(self, USERNAME, PASSWORD)
    except Exception as e:
      print(e)
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
  def __init__(self, inputs, fields, cmds):
    top = Tk()
    top.geometry('{}x{}'.format(500, 200))
    top.title('Select Mail Service')
    for inpt in inputs:
      btn(top, inpt[0], inpt[1], inpt[2], fields, cmds)
    but = Button(top, text='Quit', command = (lambda: self.gui_quit(top)))
    but.pack(side=BOTTOM)
    top.mainloop()
    
"""
Class for button that can take action
"""
class btn():
  def __init__(self, top, label, host, username, fields, cmds):
    row = Frame(top)
    but = Button(row, text=label, command = (lambda: self.start_service(host, username, fields, cmds)))
    but.pack()
    row.pack()
  def start_service(self, host, username, fields, cmds):
    mail = mail_client(host)
    req_pw(mail, username, fields, cmds)
    boxes = mail.get_boxes()
    top = req_query(boxes, fields, cmds, mail)


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
  def __init__(self, mail, USERNAME, fields, cmds):
    top = Tk()
    top.geometry('{}x{}'.format(500, 200))
    top.title('Login')
    Label(top, text='Enter Password').pack(side=TOP)
    ent = Entry(top, show="*")
    ent.pack(side=TOP, expand=YES)
    btn = Button(top, text='Submit', command = (lambda: self.login(mail, USERNAME, ent.get(), top)))
    btn.pack(side=LEFT)
    top.bind('<Return>', (lambda event: self.login(mail, USERNAME, ent.get(), top, fields, cmds)))
    Button(top, text='Quit', command = (lambda: self.gui_quit(top))).pack(side=RIGHT)
    top.mainloop()
    return()
  def login(self, mail, USERNAME, PASSWORD, top, fields, cmds):
    if((mail.login(USERNAME, PASSWORD)) == True):
      top.destroy()
      boxes = mail.get_boxes()
      top = req_query(boxes, fields, cmds, mail)
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
    top.mainloop()
    return
  def response(self, top, ent):
    self.respnse = ent
    top.destroy()
    return
  def get_val(self):
    return self.respnse

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
Class for GUI window that collects information for the query and then calls the
method that is the main processing loop when the user submits input.
"""
class req_query(MyGui):
  def __init__(self, boxlst, fields, cmds, mail):
    top = Tk()
    top.geometry('{}x{}'.format(500, 600))
    top.title('Enter Query')
    ents, s_menu, a_menu = self.make_query(top, fields, boxlst, cmds)
    top.bind('<Return>', (lambda event: self.fetch(ents, s_menu, a_menu, top, boxlst, fields, mail)))
    Button(top, text='Submit', command = (lambda: self.fetch(ents, s_menu, a_menu, top, boxlst, fields, mail))).pack(side=LEFT)
    Button(top, text='Quit', command = (lambda: self.gui_quit(top))).pack(side=RIGHT)
    top.mainloop()
    return
  
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
    return entries, s_menu, a_menu

  def on_press(self):
    #print('radio button %s selected' % self.var.get())
    pass
  
  def fetch(self, ents, s_menu, a_menu, top, boxes, fields, mail):
    s_box = s_menu.get_val()
    cmd = self.var.get()
    a_box = a_menu.get_val() 
    query = {}
    i = 0
    for entry in ents:
      query[fields[i]] = entry.get()
      i += 1
    self.loop(s_box, query, cmd, a_box, boxes, mail)
    return

  def loop(self, mailbox, query, cmd, a_box, boxlst, mail):

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
      try:
        mail.select(mailbox)
      except Exception as e:
        print(e)
        return
      #Perform search
      try:
        typ, lst=mail.search(None, '%s' % search_query)
      except Exception as e:
        print('mailbox = %s, exception = %s' % (mailbox,e))
        return
      lst=lst[0].decode('utf-8')
      lst=lst.split( )
    else:
      i = 0
      box = a_box
      for mailbox in (boxlst):
        if(box == mailbox or mailbox == 'ALL'): continue
        try:
          mail.select(mailbox)
        except Exception as e:
          print(e)
          return
        #Perform search
        try:
          typ, tmp = mail.search(None, '%s' % search_query)
        except Exception as e:
          print('mailbox = %s, exception = %s' % (mailbox,e))
          return
        tmp = tmp[0].decode('utf-8')
        tmp = tmp.split( )
        for a in (tmp):
          i+=1
          mail.copy(a, box)
      status('%i Messages found.' % i)
      return i

    #If messages were found ask for what to do, else inform user that not messages matchedthe query
    if(len(lst)==0):
      status('No messages that matched query.')
      return
    
    else:
      
      ans = cmd
      #Delete
      if ans == 'delete':
        res = req_input('%i Messages found, do you really want to delete these messages? (y/n)' % len(lst))
        ans = res.get_val()
        if(ans == 'y' or ans == 'Y'):
          for a in lst:
            try:
              typ, response = mail.store(a,  '+FLAGS', r'(\Deleted)')
            except Exception as e:
              print(e)
        return len(lst)

      #Move - actually copy and delete
      elif ans == 'move':
        status('%i Messages found.' % len(lst))
        box = a_box
        success = 1
        for a in lst:
          try:
            mail.copy(a, box)
          except Exception as e:
            print(e)
            success = 0
        #Only delete if copy succeeded
        if(success == 1):
          for a in lst:
              try:
                typ, response = mail.store(a,  '+FLAGS', r'(\Deleted)')
              except Exception as e:
                print(e)
        return len(lst)

      #Copy
      elif ans == 'copy':
        status('%i Messages found. Copied to %s' % (len(lst), a_box))
        for a in lst:
          try:
            mail.copy(a, a_box)
          except Exception as e:
            print(e)
        return len(lst)

      #Fetch message
      elif ans == 'fetch':
        status('%i Messages found.' % len(lst))
        for a in lst:
          try:
            typ, data = mail.fetch(a, '(BODY.PEEK[TEXT])')
          except Exception as e:
            print (e)
          print(data)
        return len(lst)
          
