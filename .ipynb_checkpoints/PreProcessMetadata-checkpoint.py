#!/usr/bin/env python
# coding: utf-8

# In[1]:


from PyPDF2 import PdfFileReader, PdfFileWriter
import fitz
import os
import pathlib
import pandas as pd
import numpy as np


# In[2]:


# initialerstellung der csv mit allen original PDF's
def read_paper_meta(path):
    paper_path = str(path) + "PDF"
    p = pathlib.Path(path)
    pp = pathlib.Path(paper_path)
    pdf_names = []
    meta_author = []
    meta_title = []
    meta_date = []
    meta_conference = []
    meta_check = []
    meta_list = []
    files_path = list(pp.glob('*.pdf'))
    is_checked = True
    
    
    #Itertion über alle files
    for file in files_path:
        meta_control = pd.read_excel(str(path) + 'metadata_list.xlsx') # was wenn Datei noch nicht existiert?
        cur_reader = PdfFileReader(file)
        cur_pdf_name = pathlib.Path(file).name #holen PDF Name   
        
        if(cur_pdf_name in meta_control.values):
            cur_index = meta_control.loc[meta_control['PDF'] == cur_pdf_name]
            if(pd.isna(cur_index.Check.iloc[0])): #wenn Check bei der PDF leer, dann check auf False
                is_checked = False
        #Falls name der Datei nicht in der Excel, hole die Metadaten und speicher diese weg     
        if(cur_pdf_name not in meta_control.values):
            is_checked = False
            cur_writer = PdfFileWriter() # aktuelle PDF schreiben können
            cur_metadata = cur_reader.getDocumentInfo()
            cur_writer.appendPagesFromReader(cur_reader)
            cur_writer.addMetadata(cur_metadata)
            pdf_names.append(cur_pdf_name)
            
            if('/Title' in cur_metadata.keys()):
                meta_title.append(cur_metadata.title)
            else:
                cur_writer.addMetadata({'/Title':''})
                open(file, 'wb')
                cur_writer.write(file)
                cur_reader = PdfFileReader(file)
                cur_metadata = cur_reader.getDocumentInfo()
                meta_title.append(cur_metadata.title)
                        
            if('/Author' in cur_metadata.keys()):
                meta_author.append(cur_metadata.author)
            else:
                cur_writer.addMetadata({'/Author':''})
                open(file, 'wb')
                cur_writer.write(file)
                cur_reader = PdfFileReader(file)
                cur_metadata = cur_reader.getDocumentInfo()
                meta_author.append(cur_metadata.author)
                
            if('/CreationDate' in cur_metadata.keys()):
                meta_date.append(cur_metadata['/CreationDate'])
            else:
                cur_writer.addMetadata({'/CreationDate':''})
                open(file, 'wb')
                cur_writer.write(file)
                cur_reader = PdfFileReader(file)
                cur_metadata = cur_reader.getDocumentInfo()
                meta_date.append(cur_metadata['/CreationDate'])
            
            if('/ConferenceName' in cur_metadata):   
                meta_conference.append(cur_metadata['/ConferenceName'])
            else:
                cur_writer.addMetadata({'/ConferenceName':''})
                open(file, 'wb')
                cur_writer.write(file)
                cur_reader = PdfFileReader(file)
                cur_metadata = cur_reader.getDocumentInfo()
                meta_conference.append(cur_metadata['/ConferenceName'])    
                
            meta_check.append('')

            #Erstellung Dictionary mit den Metadaten der PDF's
            meta_list = {'PDF': pdf_names,
                        'Titles': meta_title,
                        'Authors': meta_author,
                        'Date': meta_date,
                        'Conference': meta_conference,
                        'Check': meta_check}
            #Erstellung als DataFrame aus Dictionary
            df_meta = pd.DataFrame(meta_list)
            #Zusammenfügen der bereits existierenden Datei und den neuen Metadaten
            meta_control = pd.concat([meta_control, df_meta])
            #Ausgabe Excel
    meta_control.to_excel(str(path) + 'metadata_list.xlsx', index=False, header=True)     
            #Öffnen der Excel falls unvollständig
            #os.system("start EXCEL.EXE " + str(path) + "metadata_list.xlsx")
            #raise Exception('Anpassen der Metadaten wegen neuer Datei notwendig. Datei wird geöffnet.\n\t\tAnschließend Programm neustarten.')
    #weitere Prüfung auf Check, dann auch öffnen der Datei   
    if(not is_checked):
        os.system("start EXCEL.EXE " + str(path) + "metadata_list.xlsx")
        raise Exception('Anpassen der Metadaten in Datei notwendig. Datei wird geöffnet.\n\t\tAnschließend Programm neustarten.')
    
    return(meta_control)


# In[ ]:


# Anpassung der Metadaten in den eigentlichen PDF's:
#hier auch Anpassen der Metadaten eines aim&scope, da soll der Name der Konferenz noch rein. Über match?
def write_paper_meta(path):
    paper_path = str(path) + "PDF/"
    #Einlesen der Excel
    excel_meta = pd.read_excel(str(path) + '/metadata_list.xlsx')
    
    #Iteration über jeden Eintrag und Veränderung der Metadaten für jeweilige PDF anhand der Einträge in Excel
    for x in range(len(excel_meta)):
        cur_pdf = excel_meta['PDF'][x] #Name der PDF  
        cur_pdf_full = paper_path + cur_pdf #voller Pfad der jeweiligen PDF
        cur_reader = PdfFileReader(cur_pdf_full) #aktuelle PDF lesen können
        cur_writer = PdfFileWriter() # aktuelle PDF schreiben können
        cur_writer.appendPagesFromReader(cur_reader)
        cur_metadata = cur_reader.getDocumentInfo() #Metadaten der aktuellen PDF holen
        cur_writer.addMetadata(cur_metadata) #Metadaten der aktuellen PDF ändern
        cur_writer.addMetadata({"/Title": excel_meta['Titles'][x]})
        cur_writer.addMetadata({"/Author": excel_meta['Authors'][x]})
        #custom Metadata
        cur_writer.addMetadata({"/CreationDate": str(excel_meta['Date'][x])})
        cur_writer.addMetadata({"/ConferenceName": excel_meta['Conference'][x]})
        with open(cur_pdf_full, "wb") as fp:
            cur_writer.write(fp)
    


# In[1]:


def write_conference_meta(path, pdf_meta):
    
    
    conference_path = str(path) + "/AimsAndScope"
    p_con = pathlib.Path(conference_path)
    files_path = list(p_con.glob('*.pdf'))

    for x in range(len(pdf_meta)):
        cur_conference = pdf_meta['Conference'][x]
        for file in files_path:
            cur_reader = fitz.open(file)
            text = ''
            for page in cur_reader:  
                text += (page.get_text("text"))
            if cur_conference.lower() in text.lower(): #funktioniert noch nicht so ganz wenn man im Text sucht, aber wenn man über PDF Namen geht schon. Was ist besser?
                cur_reader = PdfFileReader(file) #aktuelle PDF lesen können'
                cur_writer = PdfFileWriter() # aktuelle PDF schreiben können
                cur_writer.appendPagesFromReader(cur_reader)
                cur_metadata = cur_reader.getDocumentInfo() #Metadaten der aktuellen PDF holen
                cur_writer.addMetadata(cur_metadata) #Metadaten der aktuellen PDF ändern
                cur_writer.addMetadata({"/Title": cur_conference})
                with open(file, "wb") as fp:
                    cur_writer.write(fp)
