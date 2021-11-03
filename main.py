import argparse
import pandas as pd
import os
import pysftp
import json
import logging
import paramiko
from datetime import datetime
import re
import win32com.client
import glob

from modules import transform


def __main__(args) :
    # mettre le verbose dans chaque fonction
    if args.domaine not in ["covid", "dentiste", "ehpad","med", "ra", "sf", "lbm", "consolide_publie", "tout"] :
        print(" - - - Erreur : Domaine inconnu. Veuillez sélectionner un domaine existant.")
        return
    if args.verbose :
        print(" - - Verbose active")
    # domaine covid
    if args.domaine=='covid':
        if args.commande=='import':
            for fn_covid in recent_files_covid:
                import_files(fn_covid, verbose=args.verbose)
            print("Les fichiers covid ont bien été importés")
        elif args.commande=='transform_export':
            for fn_covid in recent_files_covid:
                transformed_file=transform_files(fn_covid, verbose=args.verbose)
                export_files(transformed_file, fn_covid, verbose=args.verbose)
            print("Traitement des fichiers covid terminé")
        else :
            print(" - - - Erreur : commande inconnue pour le domaine covid. Veuillez sélectionner une commande existante.")
    # domaine dentiste
    if args.domaine=='dentiste':
        if args.commande=='import':
            for fn_dentiste in recent_files_dentiste:
                import_files(fn_dentiste, verbose=args.verbose)
            print("Les fichiers dentiste ont bien été importés")
        elif args.commande=='transform_export':
            for fn_dentiste in recent_files_dentiste:
                transformed_file=transform_files(fn_dentiste, verbose=args.verbose)
                export_files(transformed_file, fn_dentiste, verbose=args.verbose)
            print("Traitement des fichiers dentiste terminé")
        else :
            print(" - - - Erreur : commande inconnue pour le domaine dentiste. Veuillez sélectionner une commande existante.")
    # domaine ehpad
    if args.domaine=='ehpad':
        if args.commande=='import':
            for fn_ehpad in recent_files_ehpad:
                import_files(fn_ehpad, verbose=args.verbose)
            print("Les fichiers ehpad ont bien été importés")
        elif args.commande=='transform_export':
            for fn_ehpad in recent_files_ehpad:
                transformed_file=transform_files(fn_ehpad, verbose=args.verbose)
                export_files(transformed_file, fn_ehpad, verbose=args.verbose)
            print("Traitement des fichiers ehpad terminé")
        else :
            print(" - - - Erreur : commande inconnue pour le domaine ehpad. Veuillez sélectionner une commande existante.")
    # domaine laboratoire de biologie médicale
    if args.domaine=='lbm':
        if args.commande=='import':
            for fn_lbm in recent_files_lbm:
                import_files(fn_lbm, verbose=args.verbose)
            print("Les fichiers lbm ont bien été importés")
        elif args.commande=='transform_export':
            for fn_lbm in recent_files_lbm:
                transformed_file=transform_files(fn_lbm, verbose=args.verbose)
                export_files(transformed_file, fn_lbm, verbose=args.verbose)
            print("Traitement des fichiers lbm terminé")
        else :
            print(" - - - Erreur : commande inconnue pour le domaine lbm. Veuillez sélectionner une commande existante.")
    # domaine médecin
    if args.domaine=='med':
        if args.commande=='import':
            for fn_med in recent_files_med:
                import_files(fn_med, verbose=args.verbose)
            print("Les fichiers médecin ont bien été importés")
        elif args.commande=='transform_export':
            for fn_med in recent_files_med:
                transformed_file=transform_files(fn_med, verbose=args.verbose)
                export_files(transformed_file, fn_med, verbose=args.verbose)
            print("Traitement des fichiers médecin terminé")
        else :
            print(" - - - Erreur : commande inconnue pour le domaine lbm. Veuillez sélectionner une commande existante.")
    # domaine résidence autonome
    if args.domaine=='ra':
        if args.commande=='import':
            for fn_ra in recent_files_ra:
                import_files(fn_ra, verbose=args.verbose)
            print("Les fichiers résidence autonome ont bien été importés")
        elif args.commande=='transform_export':
            for fn_ra in recent_files_ra:
                transformed_file=transform_files(fn_ra, verbose=args.verbose)
                export_files(transformed_file, fn_ra, verbose=args.verbose)
            print("Traitement des fichiers résidence autonome terminé")
        else :
            print(" - - - Erreur : commande inconnue pour le domaine ra. Veuillez sélectionner une commande existante.")
    # domaine sage-femme
    if args.domaine=='sf':
        if args.commande=='import':
            for fn_sf in recent_files_sf:
                import_files(fn_sf, verbose=args.verbose)
            print("Les fichiers sage-femme ont bien été importés")
        elif args.commande=='transform_export':
            for fn_sf in recent_files_sf:
                transformed_file=transform_files(fn_sf, verbose=args.verbose)
                export_files(transformed_file, fn_sf, verbose=args.verbose)
            print("Traitement des fichiers sage-femme terminé")
        else :
            print(" - - - Erreur : commande inconnue pour le domaine lbm. Veuillez sélectionner une commande existante.")
    # domaine consolidation
    if args.domaine=='consolide_publie':
        if args.commande=='sftp':
            combined_name, combined_path = consolidate_files(verbose=args.verbose)
            transport_sftp(combined_name, combined_path, verbose=args.verbose)
        else :
            print(" - - - Erreur : commande inconnue pour le domaine consolide_publie. Veuillez sélectionner une commande existante.")
    # domaine tout
    if args.domaine=='tout':
        if args.commande=='tout':
            process_all(verbose=args.verbose)
        elif args.commande=='supprimer':
            delete_all(verbose=args.verbose)
        else :
            print(" - - - Erreur : commande inconnue pour le domaine tout. Veuillez sélectionner une commande existante.")

def read_config_sftp(path_in, server_name) :
    with open(path_in) as f:
        dict_ret = json.load(f)
    L_ret = dict_ret["sftp"]
    server_config = {}
    for server in L_ret :
        if server["server"] == server_name :
            server_config = server.copy()
    logging.info("Lecture config SFTP " + path_in + ".")
    return server_config

config="config/config.json"
server_in_sftp = read_config_sftp(config,"ATLASANTE SFTP DEPOT")

host = server_in_sftp["host"]
username = server_in_sftp["username"]
password = server_in_sftp["password"]
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None 

def read_config_mail(path_in) :
    with open(path_in) as f:
        dict_ret = json.load(f)
    L_ret = dict_ret["mail"]
    mail_config={}
    for mail in L_ret :
        mail_config = mail.copy()
    return mail_config

mail_config=read_config_mail(config)

mail_to=mail_config["to"]
mail_CC=mail_config["CC"]

# Connexion au sftp
sftp = pysftp.Connection(host=host, username=username, password=password, port=2222, cnopts=cnopts) 

# Récupération des noms des fichiers sources
sftp.cwd('commandes_officines/fichiers_source/')
directory_structure = sftp.listdir_attr()
sftp.close()
filenames = [attr.filename for attr in directory_structure]

# Cherche la date dans le nom du fichier
date_pattern = re.compile(r'(?P<date>\d{12})')
def get_date(filename):
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
            if len(weeks)!=0:
                recent_files.append(recent_file)
            weeks.append(week)
        recent_file=file
    recent_files.append(recent_file)
    return recent_files

# Récupération des fichiers covid les plus récents pour chaque semaine

def get_recent_files_covid():
    filenames_covid=[]
    for file in filenames:
        if file.startswith("PHARMA-SI_Commandes_officine_COVID_"):
            filenames_covid.append(file)
    recent_files_covid=get_recent_files(filenames_covid)
    return recent_files_covid
    
recent_files_covid = get_recent_files_covid()

# Récupération des fichiers dentiste les plus récents pour chaque semaine
  
def get_recent_files_dentiste():
    filenames_dentiste=[]
    for file in filenames:
        if file.startswith("PHARMA-SI_Commandes_officine_dentistes_COVID_"):
            filenames_dentiste.append(file)
    recent_files_dentiste=get_recent_files(filenames_dentiste)
    return recent_files_dentiste

recent_files_dentiste = get_recent_files_dentiste()

# Récupération des fichiers EHPAD les plus récents pour chaque semaine
  
def get_recent_files_ehpad():
    filenames_ehpad=[]
    for file in filenames:
        if file.startswith("PHARMA-SI_Commandes_officine_ehpads_COVID_"):
            filenames_ehpad.append(file)
    recent_files_ehpad=get_recent_files(filenames_ehpad)
    return recent_files_ehpad

recent_files_ehpad = get_recent_files_ehpad()

# Récupération des fichiers médecins les plus récents pour chaque semaine
  
def get_recent_files_med():
    filenames_med=[]
    for file in filenames:
        if file.startswith("PHARMA-SI_Commandes_officine_medecins_COVID_"):
            filenames_med.append(file)
    recent_files_med=get_recent_files(filenames_med)
    return recent_files_med

recent_files_med = get_recent_files_med()

# Récupération des fichiers résidences autonomes les plus récents pour chaque semaine
  
def get_recent_files_ra():
    filenames_ra=[]
    for file in filenames:
        if file.startswith("PHARMA-SI_Commandes_officine_residences_autonomies_COVID_"):
            filenames_ra.append(file)
    recent_files_ra=get_recent_files(filenames_ra)
    return recent_files_ra

recent_files_ra = get_recent_files_ra()

# Récupération des fichiers sage-femmes les plus récents pour chaque semaine
  
def get_recent_files_sf():
    filenames_sf=[]
    for file in filenames:
        if file.startswith("PHARMA-SI_Commandes_officine_sages_femmes_COVID_"):
            filenames_sf.append(file)
    recent_files_sf=get_recent_files(filenames_sf)
    return recent_files_sf

recent_files_sf = get_recent_files_sf()

# Récupération des fichiers laboratoire de biologie médicale les plus récents pour chaque semaine
  
def get_recent_files_lbm():
    filenames_lbm=[]
    for file in filenames:
        if file.startswith("PHARMA-SI_Commandes_officine_lbms_COVID_"):
            filenames_lbm.append(file)
    recent_files_lbm=get_recent_files(filenames_lbm)
    return recent_files_lbm

recent_files_lbm = get_recent_files_lbm()

# Importation des fichiers 

def import_files(filename, verbose=True):

    # Connexion au sftp
    sftp = pysftp.Connection(host=host, username=username, password=password, port=2222, cnopts=cnopts) 
    # Téléchargement des fichiers source en local depuis sftp
    local_dir='fichiers_source/'
    local_path=os.path.join(local_dir, filename)
    sftp_dir='commandes_officines/fichiers_source/'
    path_sftp=os.path.join(sftp_dir, filename)
    # Si le fichier existe déjà, le supprimer
    if os.path.exists(local_path)==True:
        os.remove(local_path)
    sftp.get(path_sftp, local_path)
    sftp.close()
    

# Transformation des fichiers

def transform_files(filename, verbose=True):

    local_dir='fichiers_source/'
    local_path=os.path.join(local_dir, filename)
    pharma=pd.read_csv(local_path, dtype={"FINESS Géo. Officine": object}, delimiter = ';', encoding='latin-1', error_bad_lines=False)
    transform.adjust(pharma)
    df2=transform.pivot(pharma)
    df3=transform.mise_en_forme(df2, filename)
    return df3

# Exportation des fichiers cible en local

def export_files(transformed_file, filename, verbose=True):

    fileBaseName = os.path.basename(filename).split('.')[0]
    newFilename = fileBaseName + '_cible.csv'
    path2='fichiers_cible'
    new_path=os.path.join(path2, newFilename)
    transformed_file.to_csv(new_path, sep=';', index=False, encoding='latin-1')

# Consolidations des fichiers :

def consolidate_files(verbose=True):
    
    print("\n- - Consolidation des fichiers - -")
    # Création du fichier consolidé en local
    path2='fichiers_cible'
    files = os.listdir('fichiers_cible')
    # On ne prend que les fichiers csv
    csv_files=[]
    for file in files:
        extension=file.split('.')[1]
        if extension=='csv':
            csv_files.append(file)
    combined_csv = pd.concat([pd.read_csv(os.path.join(path2, f), dtype={"FINESS Géo. Officine": object, "Rang vaccinal prévu": object, "Nb flacons commandés": int}, delimiter = ';', encoding='latin-1', error_bad_lines=False) for f in csv_files ])
    combined_csv.drop('ID UNIQUE', axis=1, inplace=True) 
    combined_csv.drop('Nom PS', axis=1, inplace=True) 
    combined_csv.drop('Prénom PS', axis=1, inplace=True) 
    combined_csv.drop('Téléphone Fixe Officine', axis=1, inplace=True) 
    combined_csv.drop('Téléphone Portable Officine', axis=1, inplace=True) 
    combined_csv.drop('Spécialité PS', axis=1, inplace=True) 
    combined_csv.rename(columns={"FINESS Géo. Officine": "finess"}, inplace=True)
    combined_csv.rename(columns={"Libellé Officine": "labelOfficine"}, inplace=True)
    combined_csv.rename(columns={"Code Postal Officine": "codePostalOfficine"}, inplace=True)
    combined_csv.rename(columns={"Code CIP Officine": "codeCIPOfficine"}, inplace=True)
    combined_csv.rename(columns={"Nom Etablissement": "nomEtablissement"}, inplace=True)
    combined_csv.rename(columns={"FINESS Géo. Etablissement": "finessEtablissement"}, inplace=True)
    combined_csv.rename(columns={"N° RPPS": "rpps"}, inplace=True)
    combined_csv.rename(columns={"Type PS": "typePS"}, inplace=True)
    combined_csv.rename(columns={"Rang vaccinal prévu": "rangVaccinalPrevu"}, inplace=True)
    combined_csv.rename(columns={"Label UCD": "vaccin"}, inplace=True)
    combined_csv.rename(columns={"Modalite commande": "modaliteCommande"}, inplace=True)
    combined_csv.rename(columns={"Date de création de la commande": "dateCreationCommande"}, inplace=True)
    combined_csv.rename(columns={"Date de dernière modification de la commande": "dateEditionCommande"}, inplace=True)
    combined_csv.rename(columns={"Date de livraison à l'officine": "dateLivraisonOfficine"}, inplace=True)
    combined_csv.rename(columns={"Nombre article": "nombreArticle"}, inplace=True)
    combined_csv.rename(columns={"Email Officine": "mailOfficine"}, inplace=True)

    # Exportation du fichier consolidé nommé avec la date du jour
    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    combined_name= 'PHARMA-SI_Commandes_officine_consolide_' + date.split('-')[0] +'.csv'
    combined_path=os.path.join('fichiers_consolidés', combined_name)
    combined_csv.to_csv(combined_path, sep=';', index=False, encoding='latin-1')
    print("Consolidation des fichiers terminé")

    return combined_name, combined_path

def send_mail():
    #Envoi d'un email
    print("\n- -Envoi du mail de confirmation - -")
            
    outlook = win32com.client.Dispatch('outlook.application')
    #appeler l'application outlookk

    mail = outlook.CreateItem(0)
    #creer un mail

    mail.To = mail_to
    mail.Subject = 'Commandes officines Test'
    mail.Body = '''Bonjour,

Nous vous informons que le fichier consolidé des commandes officines vient d'être transféré sur le serveur sftp au répertoire /commandes_officines/fichiers_cible. 

Cordialement.
    '''
    mail.CC=mail_CC

    mail.Send()
    print("Le mail de confimation a bien été envoyé")

# Transport du fichier consolidé sur le sftp

def transport_sftp(combined_name, combined_path, verbose=True):

    print("\n- - Transport du fichier consolidé sur le sftp - -")
    sftp = pysftp.Connection(host=host, username=username, password=password, port=2222, cnopts=cnopts) 
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
    #send_mail()


def process_all(verbose=True):

    # Traitement des fichiers covid
    print("\n- - Traitement des fichiers covid - -")
    for fn_covid in recent_files_covid:
        import_files(fn_covid, verbose=verbose)
        transformed_file=transform_files(fn_covid, verbose=verbose)
        export_files(transformed_file, fn_covid, verbose=verbose)
    print("Traitement des fichiers covid terminé")

    print("\n- - Traitement des fichiers dentiste - -")
    # Traitement des fichiers dentistes
    for fn_dentiste in recent_files_dentiste:
        import_files(fn_dentiste, verbose=verbose)
        transformed_file=transform_files(fn_dentiste, verbose=verbose)
        export_files(transformed_file, fn_dentiste, verbose=verbose)
    print("Traitement des fichiers dentiste terminé")
    
    # Traitement des fichiers ehpad
    print("\n- - Traitement des fichiers ehpad - -")
    for fn_ehpad in recent_files_ehpad:
        import_files(fn_ehpad, verbose=verbose)
        transformed_file=transform_files(fn_ehpad, verbose=verbose)
        export_files(transformed_file, fn_ehpad, verbose=verbose)
    print("Traitement des fichiers ehpad terminé")

    # Traitement des fichiers laboratoire de biologie médicale
    print("\n- - Traitement des fichiers lbm - -")
    for fn_lbm in recent_files_lbm:
        import_files(fn_lbm, verbose=verbose)
        transformed_file=transform_files(fn_lbm, verbose=verbose)
        export_files(transformed_file, fn_lbm, verbose=verbose)
    print("Traitement des fichiers lbm terminé")

    # Traitement des fichiers médecins
    print("\n- - Traitement des fichiers médecins - -")
    for fn_med in recent_files_med:
        import_files(fn_med, verbose=verbose)
        transformed_file=transform_files(fn_med, verbose=verbose)
        export_files(transformed_file, fn_med, verbose=verbose)
    print("Traitement des fichiers médecins terminé")

    # Traitement des fichiers résidences autonomes
    print("\n- - Traitement des fichiers autonomes - -")
    for fn_ra in recent_files_ra:
        import_files(fn_ra, verbose=verbose)
        transformed_file=transform_files(fn_ra, verbose=verbose)
        export_files(transformed_file, fn_ra, verbose=verbose)
    print("Traitement des fichiers autonomes terminé")

    # Traitement des fichiers sage-femmes
    print("\n- - Traitement des fichiers sage-femme - -")
    for fn_sf in recent_files_sf:
        import_files(fn_sf, verbose=verbose)
        transformed_file=transform_files(fn_sf, verbose=verbose)
        export_files(transformed_file, fn_sf, verbose=verbose)
    print("Traitement des fichiers sage-femme terminé")

    # Consolidation
    combined_name, combined_path = consolidate_files(verbose=verbose)

    # Transfert sur le serveur sftp
    transport_sftp(combined_name, combined_path, verbose=verbose)

def delete_all(verbose = True):
    print("- Suppresion en local des fichiers /fichiers_source...")
    src_files = glob.glob('fichiers_source/*.csv')
    for src_file in src_files:
        os.remove(src_file)
    print("...fichiers de /fichiers_source supprimés")
    # Suppression des fichiers dans fichiers_cible
    print("- Suppresion en local des fichiers /fichiers_cible...")
    tgt_files = glob.glob('fichiers_cible/*.csv')
    for tgt_file in tgt_files:
        os.remove(tgt_file)
    print("...fichiers de /fichiers_cible supprimés")
    # Suppression des fichiers dans fichiers_consolidés
    print("- Suppresion en local des fichiers /fichiers_consolidés...")
    cmb_files = glob.glob('fichiers_consolidés/*.csv')
    for cmb_file in cmb_files:
        os.remove(cmb_file)
    print("...fichiers de /fichiers_consolidés supprimés")

# initialisation du parsing
parser = argparse.ArgumentParser()
parser.add_argument("domaine", type=str, help="Domaines disponibles : covid, dentiste, ehpad, lbm, med, ra, sf, consolidation_publication, tout")
parser.add_argument("commande", type=str, help="Commande à exécuter")
parser.add_argument("-v", "--verbose", help="affiche le debuggage", type=bool)
args = parser.parse_args()

date = datetime.now().strftime("%Y%m%d_%I%M%S%p")
log_filename='log/log_debug_' + date +'.log'

#logging
logging.basicConfig(level=logging.DEBUG,
                    filename=log_filename,
                    filemode="a",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    force=True)

logging.debug('This is a debug message')


# coeur
if __name__ == "__main__":
    __main__(args)


