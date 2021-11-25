# packages
from jinja2 import Template
import pandas as pd
import os
import datetime
import numpy as np

# packages envoi de mail vers serveur SMTP
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



# retourne l'emplacement du contenu html de l'email genere pour la semaine passée en paramètre
def get_email(semaine_in, path_folder = 'corpus_mails') :
    if os.path.exists(os.path.join(path_folder, semaine_in + "-PHARMA_SI_RESUME_COMMANDES.html")) :
        return os.path.join(path_folder, semaine_in + "-PHARMA_SI_RESUME_COMMANDES.html")
    else :
        return

## chargement des commandes concatenees
def load_commandes(path_folder, file_name) :
    path_file = os.path.join(path_folder, file_name)
    df_ret = pd.read_csv(path_file, sep=";", encoding="latin1", dtype=str)
    df_ret["nombreArticle"] = df_ret["nombreArticle"].apply(int)
    df_ret["dateLivraisonOfficine"] = pd.to_datetime(df_ret["dateLivraisonOfficine"], errors="coerce")
    # semaine précédente
    df_ret["dateCommande"] = df_ret["dateLivraisonOfficine"]-datetime.timedelta(7)
    df_ret.fillna("NR", inplace=True)
    return df_ret

# pour une series, calcul le nombre d'éléments uniques 

def nombre_PS(x) :
    return len(x.unique())

# cumul par semaine
def agregate_modalite(df_commandes_in, semaine_in) :
    # filtrage date
    df_ret = df_commandes_in[df_commandes_in["dateCommande"] == datetime.datetime.strptime(semaine_in, "%Y-%m-%d")].copy()
    df_ret = df_ret[df_ret["nombreArticle"] != 0]
    # regroupement par modalite
    df_ret = df_ret.groupby(by=["typePS","vaccin","modaliteCommande"], as_index=False).agg(
        {"nombreArticle" : sum, "rpps" : nombre_PS, "finess" : nombre_PS, "finessEtablissement" : nombre_PS})
    df_ret.sort_values(by=["typePS","vaccin","modaliteCommande"], inplace=True)
    return df_ret

# generation du corpus de texte à partir de jinja2
def generate_resume_df(df_commandes_modalite, semaine_in, L_config_domaine) :
    # templates utilises plus base
    template_header = "<h2>Résumé de l'opération de commande du {{semaine}}</h2>"
    template_line = "<li>{{modalite}} : {{nb_modalite}} commandés par {{nb_PS}} {{typePS}}</li>"
    template_subheader = "<h3> Commandes {{vaccin}} : {{nb_flacons_vaccin}} flacons commandés </h3>"
    template_subheader_PS = "<li> {{type_PS}} : {{nb_flacons_vaccin}} flacons commandés soit {{part_commandes}} % des commandes {{vaccin}} </li>"
    # generation de la chaine de texte
    header = Template(template_header).render({"semaine" : semaine_in})
    html_ret = "<!DOCTYPE html>\n<html>\n<body>"
    html_ret = html_ret + '\n' + header
    html_ret = html_ret + '\n' + "<ul>"
    # sous paragraphe pour chaque vaccin
    for vaccin in df_commandes_modalite["vaccin"].unique() :
        html_ret = html_ret + '\n'
        nb_flacons_vaccin_tot = df_commandes_modalite.loc[df_commandes_modalite["vaccin"] == vaccin, "nombreArticle"].sum()
        subheader = Template(template_subheader).render({"vaccin" : vaccin, 
                                                        "nb_flacons_vaccin" : nb_flacons_vaccin_tot})
        html_ret = html_ret + subheader + '\n'
        # sous paragraphe pour chaque type de PS
        for type_PS in df_commandes_modalite["typePS"].unique() :
            df_commandes_modalite_vaccin = df_commandes_modalite[(df_commandes_modalite["vaccin"] == vaccin) & (df_commandes_modalite["typePS"] == type_PS)]
            if not df_commandes_modalite_vaccin.empty :
                nb_flacons_vaccin_PS = df_commandes_modalite_vaccin["nombreArticle"].sum()
                ratio_flacons = int((nb_flacons_vaccin_PS / nb_flacons_vaccin_tot) *100)
                subheader_PS = Template(template_subheader_PS).render({"type_PS" : type_PS,
                                                        "part_commandes" : ratio_flacons,
                                                        "vaccin" : vaccin, 
                                                        "nb_flacons_vaccin" : nb_flacons_vaccin_PS})
                html_ret = html_ret + '\n' + subheader_PS
                html_ret = html_ret + '\n' + "<ul>"
                # sous paragraphe pour chaque type de modalite de commande
                for index, row in df_commandes_modalite_vaccin.iterrows():
                    html_ret = html_ret + '\n'
                    nb_PS = ""
                    # on utilise le denombrement renseigné pour renseigner le nombre d etablissement qui commandent
                    col_denombrement = "finess"
                    # utilisation de la colonne de denombrement spécifiée.
                    for config_domaine in L_config_domaine :
                        if config_domaine["domaine"] == type_PS :
                            if config_domaine["denombrement"] in ["finess", "rpps", "finessEtablissement"] :
                                col_denombrement = config_domaine["denombrement"]
                    nb_PS = str(row[col_denombrement])
                    # a partir du template, on genere la ligne pour le type de PS et la modalite de commande associée
                    line = Template(template_line).render({"modalite" : row["modaliteCommande"], 
                                                        "nb_modalite" : row["nombreArticle"],
                                                        "nb_PS" : nb_PS,
                                                        "typePS" : type_PS})
                    html_ret = html_ret + line
                html_ret = html_ret + '\n' + "</ul>"
    html_ret = html_ret + '\n' + "</ul>"
    html_ret = html_ret + '\n' + "</body>\n</html>"
    return html_ret

def save_html(html_in, folder_out, semaine_in) :
    Html_file= open(os.path.join(folder_out, semaine_in + "-PHARMA_SI_RESUME_COMMANDES.html"),"w", encoding="utf-8")
    Html_file.write(html_in)
    Html_file.close()
    return

def generate_html(combined_name_in, semaine_in, L_config_domaine, folder_out='corpus_mails', folder_in="fichiers_consolidés") :
    df_commandes = load_commandes(folder_in, combined_name_in)
    df_commandes_modalite = agregate_modalite(df_commandes, semaine_in)
    html_commandes  = generate_resume_df(df_commandes_modalite, semaine_in, L_config_domaine)
    save_html(html_commandes, folder_out, semaine_in)
    return

def send_mail(config_mail, semaine_in) :

    # Chargement des paramètres
    
    expediteur = config_mail["expediteur"]
    destinataires = config_mail["destinataires"]
    password = config_mail["password"]

    # Création de la payload
    path_html_in = get_email(semaine_in)
    if path_html_in :
        print(" - - Préparation du mail de la semaine du " + semaine_in + " ...")
    else :
        print(" - Erreur : le contenu du mail pour la semaine en cours n'a pas été forgé.")
    html_file = open(path_html_in, "r", encoding="utf-8")
    #lis tout le fichier en tant que string
    html_raw = html_file.read()
    html_file.close()
    mail_content = MIMEText(str(html_raw), "html")

    message = MIMEMultipart("alternative")
    message["Subject"] = "Semaine du " + semaine_in + " : Résumé Commande portail officine"
    message["From"] = expediteur
    message["To"] = ", ".join(destinataires)
    message.attach(mail_content)

    # Envoi
    # Création de la connexion sécurisée et envoi
    # NB : le numero de port doit etre entier
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config_mail["server_url"], int(config_mail["server_port"]), context=context) as server:
        server.login(expediteur, password)
        server.sendmail(
            expediteur, destinataires, message.as_string()
        )
        print(" - - Envoi terminé.")
    return