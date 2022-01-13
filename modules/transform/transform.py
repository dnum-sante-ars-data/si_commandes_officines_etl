import pandas as pd
import numpy as np
import os
import datetime

# recuperation des fichiers sources

def get_filenames_import(local_dir='fichiers_source/') :
    filenames = [f for f in os.listdir(local_dir) if os.path.isfile(os.path.join(local_dir, f))]
    return filenames

## Mise en forme des fichiers commandes des pharmaciens/infirmiers :

def adjust(df_in, ajustements_in):

    df_in.drop(df_in.columns[df_in.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
    
    # renommage des colonnes 
    for nom_col_in, nom_adjust in ajustements_in["rename"].items() :
        # renommage seulement si la colonne existe
        if nom_col_in in df_in :
            df_in.rename(columns={nom_col_in: nom_adjust}, inplace=True)
    if 'codeCIPOfficine' not in df_in :
        df_in.insert(4, 'codeCIPOfficine', np.nan)
    if 'nomEtablissement' not in df_in :
        df_in.insert(5, 'nomEtablissement', np.nan)
    if 'finessEtablissement' not in df_in :
        df_in.insert(6, 'finessEtablissement', np.nan)
    if 'dateEditionCommande' not in df_in :
        df_in.insert(7, 'dateEditionCommande', np.nan)
    if 'dateLivraisonOfficine' not in df_in :
        df_in.insert(8, 'dateLivraisonOfficine', np.nan)
    if 'rpps' not in df_in :
        df_in.insert(10, 'rpps', np.nan)
    if 'typePS' not in df_in :
        df_in.insert(13, 'typePS', np.nan)
    # colonnes supprimees
    for nom_col_delete in ajustements_in["delete"] :
        if nom_col_delete in df_in :
            df_in.drop(nom_col_delete, axis=1, inplace=True)
    return

## Pivot des commandes de vaccin 

def pivot(df_in):
    
    #Passage de colonne à ligne pour les differentes commandes de vaccin
    melted=df_in.melt(id_vars=['finess', 'labelOfficine', 'codePostalOfficine', "mailOfficine",
        'codeCIPOfficine', 'finessEtablissement', 'nomEtablissement', 
        'rpps', 'typePS',
        'dateCreationCommande', 'dateEditionCommande', "dateLivraisonOfficine"], var_name='modaliteCommande', value_name='nombreArticle')
    df2=melted.drop(melted[melted['nombreArticle']==0].index).reset_index(drop=True)

    return df2


#### typePS, Label UCD et Rang vaccinal prévu 

def mise_en_forme(df, name, config_domaine):

    pd.options.mode.chained_assignment = None


    # Remplissage de la colonne typePS
    df['typePS'] = "Pharmacien"
    if config_domaine["domaine"] :
        df['typePS'] = config_domaine["domaine"]
    else :
        print(" - - Attention : le type de domaine n'est pas identifie")
    # exception pour le type Infirmier
    for i in range (len(df['modaliteCommande'])):
        if 'INFIRMIER' in df['modaliteCommande'][i]:
            df['typePS'][i] = 'Infirmier'  

    # Remplissage de la colonne vaccin
    df.insert(14, 'vaccin', np.nan)

    for i in range (len(df['modaliteCommande'])):
        if 'AstraZeneca' in df['modaliteCommande'][i] or 'ASTRAZENECA' in df['modaliteCommande'][i]:
            df['vaccin'][i] = 'AstraZeneca'
        elif 'Moderna' in df['modaliteCommande'][i]:
            df['vaccin'][i] = 'Moderna'
        elif 'Janssen' in df['modaliteCommande'][i]:
            df['vaccin'][i] = 'Janssen'
        elif 'Pfizer pédiatrique' in df['modaliteCommande'][i]:
            df['vaccin'][i] = 'Pfizer Pediatrique'
        elif 'Pfizer' in df['modaliteCommande'][i]:
            df['vaccin'][i] = 'Pfizer'
        else:
             df['vaccin'][i] = 'NR'

    # Seperation de la colonne des commandes en mots 
    commande=df['modaliteCommande'].str.split(' ', expand = True)
    
    # Remplissage de la colonne rangVaccinalPrevu 
    df.insert(15, 'rangVaccinalPrevu', np.nan)
    for i in range (0, commande.shape[0]):
        for j in range (0, commande.shape[1]):
            if commande[j][i]=='injections':
                df['rangVaccinalPrevu'][i]=commande[j-1][i]+' '+ commande[j][i]

    # verification du remplissage de la colonne nombreArticle
    df["nombreArticle"] = pd.to_numeric(df["nombreArticle"], errors="coerce", downcast="integer")

    if not df[df["nombreArticle"].isna()].empty :
        print(" - - Erreur pour les modalites de commandes suivantes : ")
        print(list(df.loc[df["nombreArticle"].isna(), "modaliteCommande"].unique()))
    df["nombreArticle"] = df["nombreArticle"].fillna(0)
    return df

# verifie que les fichiers integres depuis fichiers_cibles sont bien formatés

def check_header_csv(path_in, L_columns_def) :
    ret = True
    L_columns_in = pd.read_csv(path_in, index_col=0, nrows=0, delimiter = ';', encoding='latin-1').columns.tolist()
    # verifie que la liste des colonnes du fichiers passe en param est un sous ensemble de l'autre liste
    if set(L_columns_in) <= set(L_columns_def) :
        ret = True
    else :
        ret = False
    return ret


# Consolidations des fichiers :

def consolidate_files(path2='fichiers_cible', verbose=True):
    
    print(" - - Consolidation des fichiers - -")
    # Création du fichier consolidé en local
    files = os.listdir('fichiers_cible')
    # On ne prend que les fichiers csv
    csv_files=[]
    L_columns_def = ["labelOfficine", "finess", "rpps", "typePS", 
        "codePostalOfficine", "codeCIPOfficine", "mailOfficine",
        "finessEtablissement", "nomEtablissement",
        "dateCreationCommande", "dateEditionCommande", "dateLivraisonOfficine",
        "vaccin", "modaliteCommande", "rangVaccinalPrevu", "nombreArticle"]
    for file in files:
        extension=file.split('.')[1]
        if (extension=='csv') and check_header_csv(os.path.join(path2, file), L_columns_def):
            csv_files.append(file)
    # verification qu'il y'a bien des fichiers à consolider
    if csv_files :
        combined_csv = pd.concat([pd.read_csv(os.path.join(path2, f), 
            dtype={ "finess": str, "labelOfficine" : str, 
                "codePostalOfficine" : str, "codeCIPOfficine" : str,  "mailOfficine" : str,
                "finessEtablissement" : str, "nomEtablissement" : str,
                "rpps": str, "typePS" : str, 
                "dateCreationCommande" : str, "dateEditionCommande": str, "dateLivraisonOfficine": str,
                "modaliteCommande" : str, "rangVaccinalPrevu": str, "nombreArticle": float}, 
            delimiter = ';', encoding='latin-1', error_bad_lines=False) for f in csv_files ])
    else :
        print(" - - Erreur : Consolidation des fichiers impossible : pas de fichier cible")
        return False, False
    # Exportation du fichier consolidé nommé avec la date du jour
    date = datetime.datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    combined_name= 'PHARMA-SI_Commandes_officine_consolide_' + date.split('-')[0] +'.csv'
    combined_path=os.path.join('fichiers_consolidés', combined_name)
    combined_csv.to_csv(combined_path, sep=';', index=False, encoding='latin-1', na_rep="", float_format='%.0f')

    return combined_name, combined_path

# Transformation des fichiers

def transform_files(filename, ajustements_in, config_domaine, local_dir='fichiers_source/', verbose=True):
    local_path=os.path.join(local_dir, filename)
    df1=pd.read_csv(local_path, dtype=str, delimiter = ';', encoding='latin-1', error_bad_lines=False)
    adjust(df1, ajustements_in)
    df2 = pivot(df1)
    df3 = mise_en_forme(df2, filename, config_domaine)
    return df3

# Exportation des fichiers cible en local

def export_files(transformed_file, filename, verbose=True):
    fileBaseName = os.path.basename(filename).split('.')[0]
    newFilename = fileBaseName + '_cible.csv'
    path2='fichiers_cible'
    new_path=os.path.join(path2, newFilename)
    transformed_file.to_csv(new_path, sep=';', index=False, encoding='latin-1', float_format='%.0f')