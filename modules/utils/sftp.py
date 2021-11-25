import pandas as pd
import os
import pysftp
import json
import logging
import paramiko
from datetime import datetime
import re
import subprocess
import wget

# Module pour les fonctions liées aux SFTPs

def get_filenames(sftp) :
    # Récupération des noms des fichiers sources
    sftp.cwd('commandes_officines/fichiers_source/')
    directory_structure = sftp.listdir_attr()
    filenames = [attr.filename for attr in directory_structure]
    # retour à la racine
    sftp.cwd('..')
    sftp.cwd('..')
    return filenames


# Importation des fichiers 

def import_files(sftp, filename, verbose=True, local_dir='fichiers_source/', sftp_dir='commandes_officines/fichiers_source/'):
    # Téléchargement des fichiers source en local depuis sftp
    local_path=os.path.join(local_dir, filename)
    path_sftp= sftp_dir + filename
    # Si le fichier existe déjà, le supprimer
    if os.path.exists(local_path)==True:
        os.remove(local_path)
    sftp.get(path_sftp, local_path)

# Importation des fichiers version wget pour VM CENTOS

def wget_files(filename, username="username", password="password", sftp_host="host", verbose=True, local_dir='fichiers_source/', sftp_dir='commandes_officines/fichiers_source/'):
    #dst = "/"
    dst = local_dir
    username = username
    password = password
    sftp_host = sftp_host
    #filepath = "doctolib/2021-11-03-doctolib-rdv.csv"
    filepath = sftp_dir + filename
    cmd = 'wget --directory-prefix='+dst+' --user="'+username+'" --password="'+password+'"  ftp://'+sftp_host+'/'+filepath+' --progress=bar'
    subprocess.run(cmd, shell=True)
    print(' - Commande "'+cmd+'" exécutée')

# Transport du fichier consolidé sur le sftp

def transport_sftp(sftp, combined_name, combined_path, verbose=True):

    print("\n- - Transport du fichier consolidé sur le sftp - -")
    sftp_dir2 = 'commandes_officines/fichiers_cible/'
    # Supression des anciens fichiers consolidés
    anciens_fichiers_consolides = sftp.listdir(sftp_dir2)
    for file in anciens_fichiers_consolides:
        sftp.remove(os.path.join(sftp_dir2,file))
    print("Les anciens fichiers consolidés ont été supprimés du serveur sftp") 
    # Transport du fichier
    path_sftp2=os.path.join(sftp_dir2, combined_name)
    sftp.put(combined_path, path_sftp2)
    print("Le fichier " + combined_name + " a bien été transporté sur le serveur sftp")
    return
