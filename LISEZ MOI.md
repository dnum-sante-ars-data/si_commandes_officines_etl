## Présentation

Ce dépot git contient un script proposant un modèle plus stable pour la visualisation des données de commandes de doses de vaccins par les officines.

## Dépendances 

Python 3.8.8 64-bit (conda) Librairies : argparse, pandas, numpy, os, pysftp, json, logging, paramiko, datetime, re, win32com.client

## Configuration

Le fichier de configuration config.json reprenant le template de config_demo.json est à créer et à placer dans le dossier config.

## Utilisation

Les fichiers source se trouvent dans le dossier "fichiers source" du répertoire /commandes_officines sur le serveur SFTP.

### Main.py

Les différents domaines correspondant aux types de fichiers sont les suivants : covid, dentiste, ehpad, med, ra, sf et lbm.

#### Import des fichiers

Importer les fichiers source depuis le serveur sftp :

```
python main.py [domaine_type_de_fichier] import --verbose True
```

#### Transformation et exportation des fichiers 

Transformer les fichiers en fichiers cible et les exporter localement :

```
python main.py [domaine_type_de_fichier] transform_export --verbose True
```

#### Concolidation et publication au sftp

Consolider les fichiers et publier le fichier consolidé sur le serveur sftp :
```
python main.py consolide_publie sftp --verbose True
```
Le fichier consolidé est transféré dans le dossier "fichiers cible" du répertoire /commandes_officines sur le serveur SFTP.

#### Tout traiter 

Importer, transformer et consolider tous les fichiers puis publier le fichier consolidé sur le serveur sftp :
```
python main.py tout tout --verbose True
```
Le fichier consolidé est transféré dans le dossier "fichiers cible" du répertoire /commandes_officines sur le serveur SFTP.


### Mise en forme des fichiers avec transform.py

Le fichier transform.py se trouve dans le dossier modules/transform. Il effectue une mise en forme des fichiers en 3 étapes :

- Ajustement : Renomme les colonnes si nécessaire et/ou ajoute les colonnes manquantes
- Pivot : Fait pivoter de colonne à ligne les commandes de vaccin
- Mise en forme : Remplit la colonne "Type PS", crée puis remplit les colonnes "label UCD" et "Rang vaccinal prévu" 
