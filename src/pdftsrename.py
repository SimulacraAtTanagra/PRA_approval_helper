# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 12:08:05 2020

@author: shane
"""

from admin import newest
import textract
import os


#subcomponent of timesheet scraper for pr-assist/aems for emp verifications
def tsrename(path,fname):
    pdffile = newest(path,fname)
    text=textract.process(pdffile,encoding='ascii')
    listx=str(text).split('\\r\\n')
    emplid=[i for i in listx if 'Empl.' in i][0].split(': ')[1][:8]
    y=''.join([x for x in listx if '/' in x][0].split(' ')[0].split('/'))
    z=''.join([w for w in ' '.join([x for x in listx if 'Empl' in x][0].split(': ')[1].split(' ')[1:3]) if ',' not in w]).split(' ')
    outline=f'{emplid}_{z[1]}_{z[0]}_ts_{y}.pdf'
    return(outline)
def pull_df(path,fname):
    return(iterator(extractor(path,fname)))
def extractor(path,fname):
    pdffile = newest(path,fname)
    text=textract.process(pdffile,encoding='ascii')
    listx=str(text).split('\\r\\n')
    listx=[i for i in listx if len(i)>7]
    listx=[i for i in listx if  len(i)<10]
    listx=[i for i in listx if i[0] in ['1','2','N'] and ',' not in i and '.' not in i]
    return(listx)
def iterator(listx):
    messlist=list(set([i for ix,i in enumerate(listx) if i[0] in ['1','2'] and listx[ix+1][0] not in ['N']]))
    return(messlist)
def renamer(directory_in_str,newname,filename,itera):
    if newname in [os.fsdecode(file) for file in os.listdir(os.fsencode(directory_in_str))]:
        if itera==0:
            itera+=1
            newname=newname[:-4]+str(itera)+newname[-4:]
            renamer(directory_in_str,newname,filename,itera)
        else:
            itera+=1
            newname=newname[:-5]+str(itera)+newname[-4:]
            renamer(directory_in_str,newname,filename,itera)
    else:
        oldpath=f'{directory_in_str}\\{filename}'
        newpath=f'{directory_in_str}\\{newname}'
        os.rename(oldpath,newpath)
def rename_all(directory_in_str):
    directory = os.fsencode(directory_in_str)           #defines directory as indicated string
    os.chdir(directory)                                 #navigate to directory specified
    for file in os.listdir(directory):                  #iterates over all the files here
        filename = os.fsdecode(file)                    #specifies filename from file
        if ("Crystal") in filename:                  #isolates epub for further action
            newname=tsrename(directory_in_str,filename)
            try:
                renamer(directory_in_str,newname,filename,0)
            except:
                print(f"{filename} could not be renamed to {newname}")
