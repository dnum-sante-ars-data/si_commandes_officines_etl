import argparse
import pandas as pd
import os
import pysftp
import json
import logging
import paramiko
import datetime
import re
import warnings

from modules import transform
from modules import mail
from modules import utils
from modules.mail.mail import send_mail

# suppression des futurs warning
warnings.simplefilter(action='ignore', category=FutureWarning)

# chargement de la configuration

def read_config_sftp(path_in, server_name) :
    with open(path_in, encoding="utf-8") as f:
        dict_ret = json.load(f)
    L_ret = dict_ret["sftp"]
    server_config = {}
    for server in L_ret :
        if server["server"] == server_name :
            server_config = server.copy()
    logging.info(" - Lecture config SFTP " + path_in + ".")
    return server_config

def read_config_nomenclature(path_in) :
    with open(path_in, encoding="utf-8") as f:
        dict_ret = json.load(f)
    nomenclature_fichier = dict_ret["nomenclature_fichier"]
    logging.info(" - Lecture config nomenclature " + path_in + ".")
    return nomenclature_fichier

def read_config_adjust_fichier(path_in) :
    with open(path_in, encoding="utf-8") as f:
        dict_ret = json.load(f)
    nomenclature_fichier = dict_ret["adjust_fichier"]
    logging.info(" - Lecture configuration ajustement des fichiers " + path_in + ".")
    return nomenclature_fichier

def read_config_mail(path_in) :
    with open(path_in, encoding="utf-8") as f:
        dict_ret = json.load(f)
    config_mail = dict_ret["mail"]
    logging.info(" - Lecture configuration envoi des mails " + path_in + ".")
    return config_mail

config="config/config.json"
server_in_sftp = read_config_sftp(config,"ATLASANTE SFTP DEPOT")
nomenclature_domaine = read_config_nomenclature(config)
ajustements = read_config_adjust_fichier(config)
config_mail = read_config_mail(config)

host = server_in_sftp["host"]
username = server_in_sftp["username"]
password = server_in_sftp["password"]
port = server_in_sftp["port"]
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None


# initialisation du parsing
parser = argparse.ArgumentParser()
parser.add_argument("domaine", type=str, help="Domaines disponibles : covid, dentiste, ehpad, lbm, med, ra, sf, consolidation_publication, tout")
parser.add_argument("commande", type=str, help="Commande à exécuter")
parser.add_argument("-v", "--verbose", help="affiche le debuggage", type=bool)
parser.add_argument("-d", "--date", help="Configure la date a prendre en compte pour le mail a envoye", type=str)
args = parser.parse_args()

# date et semaine en cours par defaut
date = datetime.date.today()
semaine = datetime.datetime.strftime(
    datetime.datetime.today() - datetime.timedelta(days=date.weekday()),
    "%Y-%m-%d")

#logging
log_filename='log/log_' + datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d_%H%M") +'.log'
logging.basicConfig(level=logging.DEBUG,
                    filename=log_filename,
                    filemode="a",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    force=True)

# utilitaire

def __main__(args) :
    # mettre le verbose dans chaque fonction


    # gestion de la semaine passée en paramètre
    global date
    global semaine
    
    if args.date :
        try :
            date = datetime.datetime.strptime(args.date, "%Y-%m-%d")
        except :
            print(" - Erreur : parametre date saisi invalide.")
        semaine = datetime.datetime.strftime(date - datetime.timedelta(days=date.weekday()),"%Y-%m-%d")

    print(" - Semaine sélectionnée : " + semaine + ".")
    # gestion du domaine passé en paramètre
    allowed_domaine = [ elem["domaine"] for elem in nomenclature_domaine if "domaine" in elem.keys()]
    if args.domaine == 'tout' :
        L_config_domaines = nomenclature_domaine.copy()
        print(" - - Tous les domaines sont pris en compte.")
    elif args.domaine not in allowed_domaine :
        print(" - Erreur : Domaine inconnu. Veuillez sélectionner un domaine existant.")
        return
    else :
        print(" - - Le domaine " + str(args.domaine) + " est pris en compte.")
        L_config_domaines = [elem for elem in nomenclature_domaine if elem["domaine"] == args.domaine]
    # gestion de la commande passée en paramètre
    # import des fichiers
    if args.commande == "import" :
        # Connexion au sftp
        with pysftp.Connection(host=host, username=username, password=password, port =port, cnopts=cnopts) as sftp:
            filenames_sftp = utils.sftp.get_filenames(sftp)
            for config_domaine in L_config_domaines :
                recent_files_domaine = utils.utils.get_files_prefixe(filenames_sftp, config_domaine["prefixe"])
                recent_files_domaine = utils.utils.get_recent_files(recent_files_domaine)
                # import des fichiers un par un
                for fn in recent_files_domaine :
                    # fonction pysftp :
                    #utils.sftp.import_files(sftp, fn, verbose=args.verbose)
                    # fonction à utiliser pour la VM CENTOS : 
                    utils.sftp.wget_files(fn, username=username, password=password, sftp_host=host, verbose=args.verbose)
                    print(" - - Import de " + fn + " terminé.")
                    logging.debug("Import de " + fn + " terminé.")
                print(" - - Les fichiers "  + str(config_domaine["domaine"]) + " ont bien été importés")
    # mise en forme et enregistrement dans le répertoire cible
    elif args.commande=='transform_export':
        filenames_import = transform.get_filenames_import()
        for config_domaine in L_config_domaines :
            files_import = utils.utils.get_files_prefixe(filenames_import, config_domaine["prefixe"])
            files_import = utils.utils.get_recent_files(files_import)
            # import des fichiers un par un
            for fn in files_import :
                transformed_file = transform.transform_files(fn, ajustements, config_domaine, verbose=args.verbose)
                transform.export_files(transformed_file, fn, verbose=args.verbose)
                logging.debug("Mise en forme de " + fn + ".")
            print(" - - Les fichiers "  + str(config_domaine["domaine"]) + " ont bien été mis en forme")
    # consolidation
    elif args.commande =='consolide':
        # seul le domaine 'tout' est accepté pour cette commande
        if args.domaine != 'tout' :
            print(" - Erreur : Domaine invalide pour la commande 'consolide'.")
            return
        combined_name, combined_path = transform.consolidate_files(verbose=args.verbose)
        if combined_name : 
            mail.generate_html(combined_name, semaine, L_config_domaines)
            logging.debug("Consolidation des fichiers cibles en un seul fichier.")
            print(" - Les fichiers cibles ont été consolidés")
    elif args.commande == 'consolide_publie':
        # seul le domaine 'tout' est accepté pour cette commande
        if args.domaine != 'tout' :
            print(" - - - Erreur : Domaine invalide pour la commande 'transform_export'.")
            return
        combined_name, combined_path = transform.consolidate_files(verbose=args.verbose)
        if combined_name :
            mail.generate_html(combined_name, semaine, L_config_domaines)
            print(" - Les fichiers cibles ont été consolidés")
            with pysftp.Connection(host=host, username=username, password=password, port =port, cnopts=cnopts) as sftp:
                utils.sftp.transport_sftp(sftp, combined_name, combined_path, verbose=args.verbose)
            print(" - Les fichiers cibles ont été publiés")
    # applique toutes les étapes en un seul run
    elif args.commande == 'tout':
        # Connexion au sftp
        with pysftp.Connection(host=host, username=username, password=password, port =port, cnopts=cnopts) as sftp:
            filenames_sftp = utils.sftp.get_filenames(sftp)
            for config_domaine in L_config_domaines :
                recent_files_domaine = utils.utils.get_files_prefixe(filenames_sftp, config_domaine["prefixe"])
                recent_files_domaine = utils.utils.get_recent_files(recent_files_domaine)
                # import des fichiers un par un
                for fn in recent_files_domaine :
                    # fonction pysftp :
                    #utils.sftp.import_files(sftp, fn, verbose=args.verbose)
                    # fonction optimisée pour VM CENTOS :
                    utils.sftp.wget_files(fn, username=username, password=password, sftp_host=host, verbose=args.verbose)
                    print(" - - Import de " + fn + " terminé.")
                    logging.debug("Import de " + fn + " terminé.")
                print(" - - Les fichiers "  + str(config_domaine["domaine"]) + " ont bien été importés")
                for fn in recent_files_domaine :
                    transformed_file = transform.transform_files(fn, ajustements, config_domaine, verbose=args.verbose)
                    transform.export_files(transformed_file, fn, verbose=args.verbose)
                    logging.debug("Mise en forme de " + fn + ".")
                print(" - - Les fichiers "  + str(config_domaine["domaine"]) + " ont bien été mis en forme")
            combined_name, combined_path = transform.consolidate_files(verbose=args.verbose)
            if combined_name :
                mail.generate_html(combined_name, semaine, L_config_domaines)
                print(" - Les fichiers cibles ont été consolidés")
            with pysftp.Connection(host=host, username=username, password=password, port =port, cnopts=cnopts) as sftp:
                utils.sftp.transport_sftp(sftp, combined_name, combined_path, verbose=args.verbose)
                print(" - Les fichiers cibles ont été publiés")
    elif args.commande == 'envoi_mail':
        # seul le domaine 'tout' est accepté pour cette commande
        if args.domaine != 'tout' :
            print(" - Erreur : Domaine invalide pour la commande 'nettoyer'.")
            return
        send_mail(config_mail, semaine)
    elif args.commande == 'nettoyer':
        # seul le domaine 'tout' est accepté pour cette commande
        if args.domaine != 'tout' :
            print(" - Erreur : Domaine invalide pour la commande 'nettoyer'.")
            return
        utils.clean_repertory('fichiers_consolidés',".csv")
        utils.clean_repertory('fichiers_cible',".csv")
        utils.clean_repertory('fichiers_source',".csv")
        utils.clean_repertory('corpus_mails',".html")
        print(" - Les répertoires import et cible ont bien été nettoyés")
    return




# coeur
if __name__ == "__main__":
    __main__(args)


