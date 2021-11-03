import pandas as pd
import numpy as np

## Mise en forme des fichiers commandes des pharmaciens/infirmiers :

def adjust(pharma):

    pharma.drop(pharma.columns[pharma.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
    
    if 'ID TECHNIQUE' in pharma :
        pharma.rename(columns={'ID TECHNIQUE': 'ID UNIQUE'}, inplace=True)
    if 'Date de dernière modification' in pharma :
        pharma.rename(columns={'Date de dernière modification': 'Date de dernière modification de la commande'}, inplace=True)
    if 'NOM PS' in pharma :
        pharma.rename(columns={'NOM PS': 'Nom PS'}, inplace=True)
    if 'FINESS Géo. EHPAD' in pharma :
        pharma.rename(columns={'FINESS Géo. EHPAD': 'FINESS Géo. Etablissement'}, inplace=True)
    if 'Nom EHPAD' in pharma :
        pharma.rename(columns={'Nom EHPAD': 'Nom Etablissement'}, inplace=True)
    if 'FINESS Géo. Résidence autonomie' in pharma :
        pharma.rename(columns={'FINESS Géo. Résidence autonomie': 'FINESS Géo. Etablissement'}, inplace=True)
    if 'Nom Résidence autonomie' in pharma :
        pharma.rename(columns={'Nom Résidence autonomie': 'Nom Etablissement'}, inplace=True)
    if 'FINESS Géo. Laboratoire de biologie médicale' in pharma :
        pharma.rename(columns={'FINESS Géo. Laboratoire de biologie médicale': 'FINESS Géo. Etablissement'}, inplace=True)
    if 'Nom Laboratoire de biologie médicale' in pharma :
        pharma.rename(columns={'Nom Laboratoire de biologie médicale': 'Nom Etablissement'}, inplace=True)
    
    if 'Code CIP Officine' not in pharma :
        pharma.insert(4, 'Code CIP Officine', np.nan)
    if 'FINESS Géo. Etablissement' not in pharma :
        pharma.insert(5, 'FINESS Géo. Etablissement', np.nan)
    if 'Nom Etablissement' not in pharma :
        pharma.insert(6, 'Nom Etablissement', np.nan)
    if 'N° RPPS' not in pharma :
        pharma.insert(10, 'N° RPPS', np.nan)
    if 'Nom PS' not in pharma :
        pharma.insert(11, 'Nom PS', np.nan)
    if 'Prénom PS' not in pharma :
        pharma.insert(12, 'Prénom PS', np.nan)
    if 'Type PS' not in pharma :
        pharma.insert(13, 'Type PS', np.nan)
    if 'Spécialité PS' not in pharma :
        pharma.insert(14, 'Spécialité PS', np.nan)

    if 'code UCD' in pharma :
        pharma.drop('code UCD', axis=1, inplace=True) 

## Pivot des commandes de vaccin 

def pivot(pharma):
    
    #Passage de colonne à ligne pour les differentes commandes de vaccin
    melted=pharma.melt(id_vars=['ID UNIQUE', 'FINESS Géo. Officine', 'Libellé Officine', 'Code Postal Officine', 'Code CIP Officine', 'FINESS Géo. Etablissement', 'Nom Etablissement', 'Email Officine', 'Téléphone Fixe Officine', 'Téléphone Portable Officine', 'N° RPPS', 'Nom PS', 'Prénom PS', 'Type PS', 'Spécialité PS', 'Date de création de la commande', 'Date de dernière modification de la commande', "Date de livraison à l'officine"], var_name='Modalite commande', value_name='Nombre article')
    df2=melted.drop(melted[melted['Nombre article']==0].index).reset_index(drop=True)

    return df2


#### Type PS, Label UCD et Rang vaccinal prévu 

def mise_en_forme(df, name):

    pd.options.mode.chained_assignment = None

    # Remplissage de la colonne Type PS
    if 'medecins' in name:
        df['Type PS'] = 'Medecin'
    elif 'sages_femmes' in name:
        df['Type PS'] = 'Sage-femme'
    elif 'infirmiers' in name:
        df['Type PS'] = 'Infirmier'
    elif 'ehpads' in name:
        df['Type PS'] = 'EHPAD'
    elif 'residences_autonomies' in name:
        df['Type PS'] = 'Résidence Autonome'
    elif 'dentistes' in name:
        df['Type PS'] = 'Dentiste'
    elif 'lbms' in name:
        df['Type PS'] = 'LBMS'
    else :
        for i in range (len(df['Modalite commande'])):
            if 'INFIRMIER' in df['Modalite commande'][i]:
                df['Type PS'][i] = 'Infirmier'
            else:
                df['Type PS'][i] = 'Pharmacien'  

    # Remplissage de la colonne Label UCD
    df.insert(19, 'Label UCD', np.nan)

    for i in range (len(df['Modalite commande'])):
        if 'AstraZeneca' in df['Modalite commande'][i] or 'ASTRAZENECA' in df['Modalite commande'][i]:
            df['Label UCD'][i] = 'AstraZeneca'
        elif 'Moderna' in df['Modalite commande'][i]:
            df['Label UCD'][i] = 'Moderna'
        elif 'Janssen' in df['Modalite commande'][i]:
            df['Label UCD'][i] = 'Janssen'
        elif 'Pfizer' in df['Modalite commande'][i]:
            df['Label UCD'][i] = 'Pfizer'
        else:
             df['Label UCD'][i] = 'NR'

    # Seperation de la colonne des commandes en mots 
    commande=df['Modalite commande'].str.split(' ', expand = True)
    
    # Remplissage de la colonne Rang vaccinal prévu 
    df.insert(20, 'Rang vaccinal prévu', np.nan)
    for i in range (0, commande.shape[0]):
        for j in range (0, commande.shape[1]):
            if commande[j][i]=='injections':
                df['Rang vaccinal prévu'][i]=commande[j-1][i]+' '+ commande[j][i]

    #df.drop('Modalite commande', axis=1, inplace=True)  

    return df 