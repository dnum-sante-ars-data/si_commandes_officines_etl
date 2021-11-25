import pandas as pd
import json
import logging
from datetime import datetime
import re
import os

# Module contenant des fonctions transverses pour la manipulation de fichiers

# recupere une date dans le nom d un fichier
def get_date(filename):
    date_pattern = re.compile(r'(?P<date>\d{12})')
    matched = date_pattern.search(filename)
    if not matched:
        return None
    return datetime.strptime(matched.groups('date')[0], "%Y%m%d%H%M")

#Récupère le fichier le plus recent de la semaine
def get_recent_files(filenames):
    weeks=[]
    recent_files=[]
    for file in filenames:
        date=get_date(file)
        week=date.isocalendar()[1]
        if week not in weeks:
            recent_files.append(file)
            weeks.append(week)
    return recent_files

# Récupération des fichiers avec le prefixe indique les plus récents pour chaque semaine

def get_files_prefixe(filenames, prefixe):
    filenames_prefixe=[]
    for file in filenames:
        if file.startswith(prefixe):
            filenames_prefixe.append(file)
    files_prefixe =get_recent_files(filenames_prefixe)
    return files_prefixe 

# nettoyage d'un dossier

def clean_repertory(dir_in, extension) :
    filelist = [ f for f in os.listdir(dir_in) if f.endswith(extension) ]
    for f in filelist:
        os.remove(os.path.join(dir_in, f))
    return
