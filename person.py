import re, math, sys, pdb


class person:
    def __init__(self, iname= '', istreet = '', itown = '', istate = '', zip_code='', ihome_phone = '', icell_phone = '', ibmonth = 0, ibday= 0, ibyear = 0):
        self.name = iname
        self.address = {'street':istreet, 'town':itown, 'state':istate, 'zip_code':zip_code}
        self.bday = {'month':ibmonth, 'day':ibday, 'year':ibyear}
        self.hphone = ihome_phone
        self.cphone = icell_phone

    #Access methods
    def set_name (self, name):
        self.name = name
        return
    def set_address (self, istreet, itown, istate, izip):
        self.address['street'] = istreet
        self.address['town'] = itown
        self.address['state'] = istate
        self.address['zip_code'] = izip
    def set_birthday (self, imonth, iday, iyear):
        self.bday['month'] = imonth
        self.bday['day'] = iday
        self.bday['year'] = iyear
    def set_homephone(self, ihphone):
        self.hphone = ihphone
    def set_cellphone(self, icphone):
        self.cphone = icphone
    def get_name(self):
        return(self.name)
    def get_address(self):
        return(self.address)
    def get_birthday(self):
        return(self.bday)
    def get_homephone(self):
        return(self.hphone)
    def get_cellphone(self):
        return(self.cphone)


    #Method to print the object
    def prt(self):
        print ("Name:\t\t", self.name, sep='')
        print("Address:\t", self.address['street'], sep='')
        print("\t\t", self.address['town'], sep='')
        print("\t\t", self.address['state'], ", ", self.address['zip_code'], sep='')
        print("Home phone:\t", self.hphone, sep='')
        print("Cell phone:\t", self.cphone, sep='')
        print("Birthdate:\t", self.bday['month'], "-", self.bday['day'], "-", self.bday['year'], sep='')
        print("\n")


#Subroutine to edit a person object
def edit_record(ref):
    while(True):
        ans = input("What field do you want to edit(name/address/home phone/cell phone/birth date):")
        if ans == 'name':
            name = input("Enter new name:")
            ref.set_name(name)
        elif ans == 'address':
            street = input("Enter street address: ")
            town = input("Enter town: ")
            state = input("Enter state: ")
            while(True):
                zip_code = input("Enter zip code: ")
                if valid_zcode(zip_code): break
            ref.set_address(street, town, state, zip_code)
        elif ans == 'home phone':
            while(True):
                num = input("Enter home phone number:")
                if valid_phone(num): break
            ref.set_homephone(num)
        elif ans == 'cell phone':
            while(True):
                num = input('Enter cell phone number:')
                if valid_phone(num): break
            ref.set_cellphone(num)
        elif ans == 'birth date':
            while(True):
                bdate = input("Enter birth date (mm-dd-yyyy):")
                if valid_date(bdate): break
            ref.set_birthday(bdate[:2], bdate[3:5], bdate[6:])
        else:
            print("Invalid input!")
            continue
        ans = input("Do you want to edit another field?")
        if ans == 'n' or ans == 'N' : break
    ref.prt()
    return

#Subroutine to print Exception message and exit
def err(e):
    print("Error {0}".format(str(e)))
    sys.exit()

#Check if a zip code is valid - only 5 digits
def valid_zcode(input):
    if re.match(r'[0-9]{5}', input) and len(input) == 5:
        return(True)
    else:
        return(False)
                     
#Check if the date is valid
def valid_date(input):
    #Days in each month
    month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if len(input) > 10:
        return(False)
    if not re.match(r'[01]{1}[0-9]{1}-[0-3]{1}[0-9]{1}-[12]{1}[0-9]{3}', input):
        return(False)
    if int(input[:2]) > 12 or int(input[:2]) < 1:
        return(False)
    if not re.match(r'[0-9]{4}', input[6:]):
        return(False)
    #Check for leap year
    fractpart, intpart = math.modf(int(input[6:])/4)
    i = 1
    #Months 0-11
    j = int(input[:2]) -1 
    #If not February or not leap year set i to 0
    if j != 1 or (fractpart !=0 and j ==1):
        i = 0
    #Add i to days in the month for the validity check
    if int(input[3:5]) > (month[j] + i)  or int(input[3:5]) < 0:
        return(False)
    return(True)

#Check if phone numbers are valid: xxx-xxx-xxxx
def valid_phone(input):
    if re.match(r'[2-9]{1}[0-9]{2}-[0-9]{3}-[0-9]{4}', input):
        return(True)
    else:
        return(False)


#Subroutine to enter new people into the database
#Return the count of people in the database
def enter(people):
    cnt = 1
    i = 0
    for j in sorted(people.keys()):
        i = j + 1
        cnt += 1
    #Gather input
    name = input("Enter Name: ")
    street = input("Enter street address: ")
    town = input("Enter town: ")
    state = input("Enter state: ")
    while(True):
        zip_code = input("Enter zip code: ")
        if valid_zcode(zip_code): break              
    while(True):
        hphone = input("Enter home phone number (xxx-xxx-xxxx): ")
        if valid_phone(hphone): break
    while(True):
        cphone = input("Enter cell phone number (xxx-xxx-xxxx): ")
        if valid_phone(cphone): break
    while(True):
        bdate = input("Enter birthdate (mm-dd-yyyy): ")
        if valid_date(bdate) : break
    people[i] = person(name, street, town, state, zip_code, hphone, cphone, bdate[:2], bdate[3:5], bdate[6:])
    return(cnt)


#Subroutine to search
def search(people):    
        result = find_obj(people)
        for index in (result):
            print("Found this record: ", index)
            people[index].prt()
            ans = input("Do you want to edit this record (y/n)?")
            if ans == 'y' or ans == 'Y':
                edit_record(people[index])
        return


#Subroutine to search
def partial_search(people):    
        result = partial_find_obj(people)
        for index in (result):
            print("Found this record: ", index)
            people[index].prt()
            ans = input("Do you want to edit this record (y/n)?")
            if ans == 'y' or ans == 'Y':
                edit_record(people[index])
        return

#Subroutine to print a filtered list of records
def filter_obj(people):
    gen_func = yield_find_obj(people)
    while(True):
        try:
            index = gen_func.__next__()
        except StopIteration:
            break
        people[index].prt()
    return

#Subroutine to find a record that uses a yeild statement
def yield_find_obj(people):
    result = []
    #Gather input
    name = input("Enter Name: ")
    street = input("Enter street address: ")
    town = input("Enter town: ")
    state = input("Enter state: ")
    zip_code = input("Enter zip code: ")
    hphone = input("Enter home phone number (xxx-xxx-xxxx): ")
    cphone = input("Enter cell phone number (xxx-xxx-xxxx): ")
    bdate = input("Enter birthdate (mm-dd-yyyy): ")
    search_obj = person(name, street, town, state, zip_code, hphone, cphone, bdate[:2], bdate[3:5], bdate[6:])
    for index in (sorted(people.keys())):
        if compare_obj(search_obj, people[index]):
            yield index
    return

#Subroutine to print a filtered list of records
def partial_filter_obj(people):
    gen_func = yield_partial_find_obj(people)
    while(True):
        try:
            index = gen_func.__next__()
        except StopIteration:
            break
        people[index].prt()
    return


def yield_partial_find_obj(people):
    result = []
    #Gather input
    name = input("Enter Name: ")
    street = input("Enter street address: ")
    town = input("Enter town: ")
    state = input("Enter state: ")
    zip_code = input("Enter zip code: ")
    hphone = input("Enter home phone number (xxx-xxx-xxxx): ")
    cphone = input("Enter cell phone number (xxx-xxx-xxxx): ")
    ans = input("Enter month of birth date: ")
    if ans == '':
        month = '..'
    else:
        month = ans
    ans = input("Enter day of birthday: ")
    if ans == '':
        day = '..'
    else:
        day = ans
    ans = input("Enter year of birth date: ")
    if ans == '':
        year = '....'
    else:
        year = ans
    search_obj = person(name, street, town, state, zip_code, hphone, cphone, month, day, year)
    for index in (sorted(people.keys())):
        if partial_compare_obj(search_obj, people[index]):
            yield(index)
    return


#Subroutine to delete record
def delete(people):
    result = find_obj(people)
    for index in (result):
        print("Found this record: ")
        people[index].prt()
        ans = input("Do you want to delete this record (y/n)?")
        if ans == 'y' or ans == 'Y':
            del(people[index])
    return


        
#Subroutine to find a record
def find_obj(people):
    result = []
    #Gather input
    name = input("Enter Name: ")
    street = input("Enter street address: ")
    town = input("Enter town: ")
    state = input("Enter state: ")
    zip_code = input("Enter zip code: ")
    hphone = input("Enter home phone number (xxx-xxx-xxxx): ")
    cphone = input("Enter cell phone number (xxx-xxx-xxxx): ")
    bdate = input("Enter birthdate (mm-dd-yyyy): ")
    search_obj = person(name, street, town, state, zip_code, hphone, cphone, bdate[:2], bdate[3:5], bdate[6:])
    for index in (sorted(people.keys())):
        if compare_obj(search_obj, people[index]):
            result.append(index)
    return(result)

def partial_find_obj(people):
    result = []
    #Gather input
    name = input("Enter Name: ")
    street = input("Enter street address: ")
    town = input("Enter town: ")
    state = input("Enter state: ")
    zip_code = input("Enter zip code: ")
    hphone = input("Enter home phone number (xxx-xxx-xxxx): ")
    cphone = input("Enter cell phone number (xxx-xxx-xxxx): ")
    ans = input("Enter month of birth date: ")
    if ans == '':
        month = '..'
    else:
        month = ans
    ans = input("Enter day of birthday: ")
    if ans == '':
        day = '..'
    else:
        day = ans
    ans = input("Enter year of birth date: ")
    if ans == '':
        year = '....'
    else:
        year = ans
    search_obj = person(name, street, town, state, zip_code, hphone, cphone, month, day, year)
    for index in (sorted(people.keys())):
        if partial_compare_obj(search_obj, people[index]):
            result.append(index)
    return(result)

#Subroutine to compare two objects, null fields match anything
def compare_obj(search_obj, target_obj):
    if (search_obj.get_name() != '') and (search_obj.get_name() != target_obj.get_name()):
        return(False)
    if (search_obj.get_address()['street'] != '') and (search_obj.get_address()['street'] != target_obj.get_address()['street']):
        return(False)
    if (search_obj.get_address()['town'] != '') and (search_obj.get_address()['town'] != target_obj.get_address()['town']):
        return(False)
    if (search_obj.get_address()['state'] != '') and (search_obj.get_address()['state'] != target_obj.get_address()['state']):
        return(False)
    if (search_obj.get_address()['zip_code'] != '') and (search_obj.get_address()['zip_code'] != target_obj.get_address()['zip_code']):
        return(False)
    if (search_obj.get_homephone() != '') and (search_obj.get_homephone() != target_obj.get_homephone()):
        return(False)
    if (search_obj.get_cellphone() != '') and (search_obj.get_cellphone() != target_obj.get_cellphone()):
        return(False)

    if (search_obj.get_birthday()['month'] != '') and (search_obj.get_birthday()['month'] != target_obj.get_birthday()['month']):
        return(False)
    if (search_obj.get_birthday()['day'] != '') and (search_obj.get_birthday()['day'] != target_obj.get_birthday()['day']):
        return(False)
    if (search_obj.get_birthday()['year'] != '') and (search_obj.get_birthday()['year'] != target_obj.get_birthday()['year']):
        return(False)
    return(True)

        
        
def partial_compare_obj(search_obj, target_obj):
    if not re.search(search_obj.get_name(), target_obj.get_name()):
        return(False)
    if not re.search(search_obj.get_address()['street'], target_obj.get_address()['street']):
        return(False)
    if not re.search(search_obj.get_address()['town'], target_obj.get_address()['town']):
        return(False)
    if not re.search(search_obj.get_address()['state'], target_obj.get_address()['state']):
        return(False)
    if not re.search(search_obj.get_address()['zip_code'], target_obj.get_address()['zip_code']):
        return(False)
    if not re.search(search_obj.get_homephone(), target_obj.get_homephone()):
        return(False)
    if not re.search(search_obj.get_cellphone(), target_obj.get_cellphone()):
        return(False)
    search_date = search_obj.get_birthday()['month']+'-'+search_obj.get_birthday()['day']+'-'+search_obj.get_birthday()['year']
    target_date = target_obj.get_birthday()['month']+'-'+target_obj.get_birthday()['day']+'-'+target_obj.get_birthday()['year']
    if not re.match(search_date, target_date):
           return(False)
    return(True)

        
#Subroutine to defragment the db
def defrag(people):
    i = 0
    limit = len(people)
    for index in (sorted(people.keys())):
        if index != i:
            people[i] = people[index]
            del(people[index])
        i += 1
    return

        
