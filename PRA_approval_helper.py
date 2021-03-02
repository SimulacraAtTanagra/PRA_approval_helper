# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 22:40:52 2020

@author: shane
"""

#this is a suite of pr-assist tools to assist in day to day automation needs
from src.seltools import mydriver,main
from time import sleep
from src.pdftsrename import pull_df



class pra(mydriver,main):
    def __init__(self,download_dir):
        self.download_dir=download_dir
        self.driver=self.setupbrowser()
 
    loginurl="https://sota.york.cuny.edu/PrAssist/PRlogon.aspx"
    unfield="ctl00_ContentPlaceHolder1_txtLoginID"
    pwfield="ctl00_ContentPlaceHolder1_txtPwd"
    submit="ctl00_ContentPlaceHolder1_ButContinue"
    un=input('username, plesae: ')
    pw=input('password, plesae: ')
    
    
    def login(self):
        self.driver.get(self.loginurl)
        self.waitfillid(self.unfield,self.un)
        self.waitfillid(self.pwfield,self.pw)
        self.main_window = self.driver.current_window_handle
        self.waitid(self.submit)
class admin(main):
    def __init__(self,driver):
        self.driver=driver
        if 'ctl00_ContentPlaceHolder1_LinkButton6' in driver.page_source:
            self.waitid('ctl00_ContentPlaceHolder1_LinkButton6')
        else:
            self.nav(0)
            self.waitid('ctl00_ContentPlaceHolder1_LinkButton6')
    def nav(self,num):
        self.waitlink(self.menu[num])
    menu=['Home','Application Setup','Application Users','Refresh T/L Balance',
          'Document Posting','Holiday Definition','Email Editor','Logoff']
    def search(self,username):
        self.waitfillid('ctl00_ContentPlaceHolder1_Deptsrch',username)
        self.waitid("ctl00_ContentPlaceHolder1_ImageButton3")
        self.xpathclick('//*[@id="ctl00_ContentPlaceHolder1_GridView1"]/tbody/tr[2]/td[5]/a')
    def get_roles(self):
        maindept=self.dropdownitembyid("ctl00_ContentPlaceHolder1_Dept")
        if self.checkbox_check("ctl00_ContentPlaceHolder1_CheckBox1"):
            try:
                addl=self.dropdownoptions("ctl00_ContentPlaceHolder1_LstMDept")
            except:
                addl=[]
        roles=self.checkbox_mass("ctl00_ContentPlaceHolder1_ch")
        return([('main',maindept),('addl',addl),('roles',roles)])
    def give_roles(self,name=None,email=None,roles=None):
        if email:
            self.waitfillid('ctl00_ContentPlaceHolder1_Deptsrch',email.split('@')[0])
            self.waitid("ctl00_ContentPlaceHolder1_ImageButton3")
        try:
            self.waitlink('view')
        except:
            self.waitid("ctl00_ContentPlaceHolder1_ButAddNew")    
        if name:
            self.waitfillid("ctl00_ContentPlaceHolder1_txtName",name)
            self.waitfillid("ctl00_ContentPlaceHolder1_Email",email)
            self.waitfillid("ctl00_ContentPlaceHolder1_txtID",email.split('@')[0])
        if roles:
            for x in roles[2]:
                self.waitid(x)
            self.dropdownselector("ctl00_ContentPlaceHolder1_Dept",roles[0][1])
            for x in roles[1][1]:
                self.dropdownselector("ctl00_ContentPlaceHolder1_DrpDept",x)
                self.waitid("ctl00_ContentPlaceHolder1_LinkButton2")
            self.waitid("ctl00_ContentPlaceHolder1_ButSave")
            self.okay2()
    def mirror(self,targetun,recipun,recipname=None):
        self.nav(2)
        self.search(targetun)
        xyz=self.get_roles()
        self.waitid("ctl00_ContentPlaceHolder1_ButCancel")
        self.nav(2)
        if recipname:       #if we include name, treat as new
            self.give_roles(name=recipname,email=recipun+"@york.cuny.edu",roles=xyz)
        else:               #otherwise treat as if they exist   
            self.give_roles(email=recipun+"@york.cuny.edu",roles=xyz)
        
        
        
    
class payroll(main):
    def __init__(self,driver):
        self.driver=driver
        if 'ctl00_ContentPlaceHolder1_LinkButton5' in driver.page_source:
            self.waitid('ctl00_ContentPlaceHolder1_LinkButton5')
        else:
            self.nav(0)
            self.waitid('ctl00_ContentPlaceHolder1_LinkButton5')
    def nav(self,num):
        self.waitlink(self.menu[num])
    menu=['Home','Review Appointments','Review Employee Action',
          'Message Center','Pay Period Control','Reports',
          'Departments and Titles','Pay Period Date Setup',
          'End of Year Process','Logoff']
    
    
    def approve_this(self,emplid):
        empldict={'ctl00_ContentPlaceHolder1_txtSSN':str(emplid)}
        self.nav(4)
        self.waitlink("Review Timesheets")
        self.data_distribute(empldict)   
        self.waitid("ctl00_ContentPlaceHolder1_butSearch")
        self.waitlink("Timesheet")
        a=self.data_collect("inputCell")             #gathering all data into a dict
        b=self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_lstPeriod").get_attribute('value')
        sleep(1)
        self.waitid("ctl00_ContentPlaceHolder1_butDelete")   #deleting offending timesheet
        sleep(1)
        self.okay2()                
        #going back to the PAF to activate, which means searching for empl and status.
        self.nav(1)
        self.search(emplid,status="PR")
        #self.dropdownselector("ctl00_ContentPlaceHolder1_lstStatus","PR")
        #self.data_distribute(empldict)               #entering emplid
        #self.waitid("ctl00_ContentPlaceHolder1_butSearch")    #gotta search bruh.
        #self.waitlink("View PAF")             #opening the PAF
        self.waitid("ctl00_ContentPlaceHolder1_butActive")    #click to activate
        sleep(2)
        self.okay2()                           #activation always requires confirmation
        
        self.nav(4)   #going back to timesheet area
        self.waitlink("Enter New Timesheets") #original is deleted, entering fresh
        self.data_distribute(empldict)               #entering emplid
        self.waitid("ctl00_ContentPlaceHolder1_butSearch")    #gotta search, my guy.
        self.waitlink("Timesheet")            #opening the timesheet
        
        #then navigating back to enter the timesheet
        self.dropdownselector("ctl00_ContentPlaceHolder1_lstPeriod",b)
        self.data_distribute(a)      #putting the values in the timesheet
        self.waitid("ctl00_ContentPlaceHolder1_butSave") #saving the timesheet
        sleep(1)
        self.okay2()
    
    def capture_sick(self,emplid,year=None):
        self.nav(2)
        self.search(emplid,year)
        sleep(1)
        datadict=self.grab_table('ctl00_ContentPlaceHolder1_GridView1')
        return(datadict)
    
    def consecutive_scrape(self,emplid):
        scrapedict=[]
        for i in range(2021,2013,-1):      
            try:
                x,y=self.scrape_sick(self.capture_sick(emplid,str(i)))
                scrapedict.append(('year',str(i)))
                scrapedict.append(('prior',x))
                scrapedict.append(('sick',y))
            except:
                pass
        return(scrapedict)
    
    def download_pr_rpt(self):
        self.waitlink("Pay Period Control")
        self.waitlink("Payroll Report")
        #going to print version
        self.waitid("CrystalReportViewer1_toptoolbar_print")
        #exporting
        self.waitlink("Export")
        sleep(3)
        self.xpathclick('//*[@title="Close Report Viewer"]')
        
    
    def fix_payroll(self,download_dir):  #shane, deprecate this method once you shore up payserv
        for i in pull_df(download_dir,'Crystal'):
            empldict={'ctl00_ContentPlaceHolder1_txtSSN':i}
            self.waitlink("Review Appointments")
            self.data_distribute(empldict)               #entering emplid
            self.dropdownselector("ctl00_ContentPlaceHolder1_lstStatus","ACTIVE")
            n="2020"
            newdict={}
            status="go"
            while True:
                self.dropdownselector("ctl00_ContentPlaceHolder1_lstYear",n)
                self.waitid("ctl00_ContentPlaceHolder1_butSearch")    #gotta search bruh.
                try:
                    self.waitlink("View PAF")             #opening the PAF
                    a=self.collect_span('//*[@id="ctl00_ContentPlaceHolder1_dspPSEID"]')
                    if len(a)<2:
                       n=str(int(n)-1)
                       if n=="2017":
                           status="stop"
                           break
                       pass
                    else:
                        newdict={"ctl00_ContentPlaceHolder1_txtPSEID":a}
                        break
                except:
                    n=str(int(n)-1)
                    if n=="2017":
                           status="stop"
                           break
                    pass
            if status!="go":
                pass
            self.waitlink("Review Appointments")
            self.search(i,year='2021',status='ACTIVE')
            self.waitid("ctl00_ContentPlaceHolder1_ButModify")
            self.data_distribute(newdict)
            self.waitid("ctl00_ContentPlaceHolder1_ButSave")
            sleep(3)
    
    def pay_period_close(self):
        #navigating to appropriate page
        self.waitlink("Pay Period Control")
        #first, stop time entry
        self.waitid('ctl00_ContentPlaceHolder1_butStopTE')
        #next, get list of all unconfirmed timesheets for further action later
        self.waitlink('Review Timesheets')
        self.waitid("ctl00_ContentPlaceHolder1_rdUnconfim")
        self.waitid("ctl00_ContentPlaceHolder1_butSearch")
        unconfirmed=self.grab_table("ctl00_ContentPlaceHolder1_GridProll")
        ###DO SOMETHING WITH THAT DATA, Shane, write it somewhere or something
        #Returning to the appropriate page
        self.waitlink("Pay Period Control")
        #confirming all timesheets
        self.waitlink("Mass Timesheet Confirmation")
        sleep(1)
        self.okay3()
        #running reports and saving
        self.waitlink("Payroll Report")
        #going to print version
        self.waitid("CrystalReportViewer1_toptoolbar_print")
        #exporting
        self.waitlink("Export")
        sleep(3)
        #returning to the appropriate page
        self.xpathclick('//*[@title="Close Report Viewer"]')
        #downloading the NPAY502 file
        self.waitlink('Generate NPAY502 File')
        #closing the prior pay period
        self.waitid("ctl00_ContentPlaceHolder1_butPostTS")
        sleep(1)
        self.okay3()
        sleep(3)
        x=self.dropdownitembyid("ctl00_ContentPlaceHolder1_lstPeriod")
        x=str(int(x)+1)

####SHANE FINISH THIS FUNCTION BROOOOO                 
        
        
        
        
        
    def scrape_sick(self,table):
        table=[i.text for i in table]
        x=max([len(i) for i in table])
        table=[i for i in table if len(i)+10<x and i!='']
        priors=[table[ix+1] for ix,i in enumerate(table) if 'Prior' in i]
        sicks=[table[ix+1] for ix,i in enumerate(table) if 'S/L Available' in i]
        prior=sum([float(i) for i in priors])
        sick=sum([float(i) for i in sicks])
        return(prior,sick)
    
    def search(self,emplid,year=None,dept=None,status=None,ctrl=None):
        flag=''
        if 'ctl00_ContentPlaceHolder1_txtID' in self.driver.page_source:
            self.waitfillid('ctl00_ContentPlaceHolder1_txtID',emplid)
            flag='a'
        elif 'ctl00_ContentPlaceHolder1_txtSSN' in self.driver.page_source:
            self.waitfillid('ctl00_ContentPlaceHolder1_txtSSN',emplid)    
            flag='b'
        if year:
            self.dropdownselector('ctl00_ContentPlaceHolder1_lstYear',str(year))
        if dept:
            self.dropdownselector("ctl00_ContentPlaceHolder1_lstDept",dept)
        if status:
            self.dropdownselector("ctl00_ContentPlaceHolder1_lstStatus",status.upper())
        if ctrl:
            self.waitfillid("ctl00_ContentPlaceHolder1_txtContrNo",ctrl)
        self.waitid("ctl00_ContentPlaceHolder1_butSearch")
        sleep(1)
        if flag=='a':
            self.xpathclick('//*[@id="ctl00_ContentPlaceHolder1_GridView1"]/tbody/tr[2]/td[6]/a')
        elif flag=='b':
            self.xpathclick('//*[@id="ctl00_ContentPlaceHolder1_grdPafList"]/tbody/tr[2]/td[10]/a')
    
    
    
    def sick_logic(scrapedict):
        #must accept list of dicts(?)
        #must do comparison based on years
        #find if consecutive
        #if consecutive, find if 0:sick = 1:prior
        #if not, "transfer" by adding to var
        #do this until current year
        #if break, var =0
        #in current year, if prior =0 but var !=0, return var
        print("scraped")
    def update_sick(self,emplid,sl):
        self.nav(2)        
        self.search(emplid)
        sleep(1)
        datadict=self.grab_table('ctl00_ContentPlaceHolder1_GridView1')
        elems=[i for i in datadict if 'ACTIVE' in i.text][0].find_elements_by_xpath(".//*")
        elem=[i for i in elems if 'ctl00_ContentPlaceHolder1_GridView1_ct' in i.get_attribute('id')][0]
        elemid=elem.get_attribute('id')
        elem.click()
        elemid=elemid.replace('lnCmd','txtSL')
        self.waitfill(elemid,sl)
        
if "__name__"=="__main__":
    download_dir = "C:\\Users\\shane\\desktop\\testpdfs" # for linux/*nix, download_dir="/usr/Public"
    home=pra(download_dir)
    home.login()
    pr=payroll(home.driver)
    pr.nav(2)
    #pr.download_pr_rpt()
    pr.fix_payroll(download_dir)
    



#driver.driver.quit()
