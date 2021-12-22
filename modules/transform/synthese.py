import pandas as pd
import numpy as np
import os
import datetime


## chargement des commandes concatenees
def load_commandes(path_folder, file_name) :
    path_file = os.path.join(path_folder, file_name)
    df_ret = pd.read_csv(path_file, sep=";", encoding="latin1", dtype=str)
    df_ret["nombreArticle"] = df_ret["nombreArticle"].apply(int)
    df_ret["dateLivraisonOfficine"] = pd.to_datetime(df_ret["dateLivraisonOfficine"], errors="coerce", format="%d/%m/%Y")
    # semaine précédente
    df_ret["dateCommande"] = df_ret["dateLivraisonOfficine"]-datetime.timedelta(7)
    df_ret.fillna("NR", inplace=True)
    return df_ret

# pour une series, calcul le nombre d'éléments uniques 

def nombre_PS(x) :
    return len(x.unique())

# cumul par semaine
def prepare_synthese(df_commandes_in) :
    # filtrage date
    df_ret = df_commandes_in[df_commandes_in["nombreArticle"] != 0]
    # regroupement par modalite
    df_ret = df_ret.groupby(by=["dateCommande","typePS","vaccin","modaliteCommande"], as_index=False).agg(
        {"nombreArticle" : sum, "rpps" : nombre_PS, "finess" : nombre_PS, "finessEtablissement" : nombre_PS})
    df_ret.sort_values(by=["dateCommande","typePS","vaccin","modaliteCommande"], inplace=True)
    return df_ret

# generation de la synthese
def generate_synthese_df(df_prep_in, L_config_domaine) :
    df_ret = df_prep_in.copy()
    # Initilisation de la colonne nombreCommanditaire
    df_ret["nombreCommanditaire"] = 0
    # utilisation de la colonne de denombrement spécifiée.
    for config_domaine in L_config_domaine :
        if config_domaine["denombrement"] in ["finess", "rpps", "finessEtablissement"] :
            df_ret.loc[df_ret["typePS"] == config_domaine["domaine"],"nombreCommanditaire"] = df_ret[config_domaine["denombrement"]]
    df_ret = df_ret[["dateCommande","typePS","vaccin","nombreArticle","nombreCommanditaire"]]
    df_ret = df_ret.pivot_table(index=["dateCommande","typePS"], columns="vaccin", values=["nombreArticle","nombreCommanditaire"], aggfunc="sum")
    # mise en forme : fusion des niveaux et alignement index en colonne
    df_ret.columns = df_ret.columns.map('-'.join).str.strip('-')
    df_ret.fillna(0, inplace=True)
    df_ret.reset_index(inplace=True)
    return df_ret


def save_synthese(df_in, folder_out='fichiers_synthese', verbose=True):
    date = datetime.datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    synthese_name = 'PHARMA-SI_Commandes_officine_synthese_' + date.split('-')[0] +'.csv'
    new_path=os.path.join(folder_out, synthese_name)
    df_in.to_csv(new_path, sep=';', index=False, encoding='latin-1', float_format='%.0f')
    return new_path

# génère le fichier de synthese de bout en bout
def generate_synthese(synthese_name_in, semaine_in, L_config_domaine, folder_out='fichiers_synthese', folder_in="fichiers_consolidés") :
    df_commandes = load_commandes(folder_in, synthese_name_in)
    df_commandes_prep = prepare_synthese(df_commandes)
    df_synthese_commande  = generate_synthese_df(df_commandes_prep, L_config_domaine)
    path_synthese = save_synthese(df_synthese_commande, folder_out=folder_out)
    return path_synthese


