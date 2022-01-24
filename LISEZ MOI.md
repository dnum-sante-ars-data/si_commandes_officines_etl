## Présentation

Ce dépot git contient un script proposant un modèle plus stable pour la visualisation des données de commandes de doses de vaccins par les officines.

## Dépendances 

Python 3.8.8 64-bit (conda) Librairies : argparse, pandas, numpy, os, pysftp, json, logging, paramiko, datetime, re, win32com.client, jinja2, smtplib, ssl

## Configuration

Le fichier de configuration config.json reprenant le template de config_demo.json est à créer et à placer dans le dossier config. Le fichier est encodé en utf-8, attention aux accents.
Ce fichier liste aussi la configuration pour la nomenclature fichiers à prendre en compte dans l'utilitaire. Attention à ne pas renseigner d'accents de préférences.

## Utilisation

Les fichiers source se trouvent dans le dossier "fichiers source" du répertoire /commandes_officines sur le serveur SFTP.
Les fichiers cible correspondent aux fichiers sources reformattés en format de sortie.
Les fichiers concaténés aggrègent les différents fichiers du répertoire 'fichiers_cible' en un seul fichier.
A partir de ce fichier concaténé, un corpus de mail pour résumer l'opération de commande est généré.
Les fichiers concaténés peuvent être publiés sur un SFTP.

### Main.py

Les différents domaines correspondant aux types de fichiers sont les suivants : la liste des domaines autorisés et des extensions de fichiers autorisées est spécifiée dans le fichier de configuration.

Exemple :

```
{
            "prefixe" : "PHARMA-SI_Commandes_officine_residences_autonomies_COVID_",
            "domaine" : "Residence Autonome",
            "denombrement" : "finessEtablissement"
        }
```
Utilisation des champs pour la configuration :
- 'prefixe' spécifie le prefixe associé à ce type de fichier
- 'domaine' le long de domaine
- denombrement indique le nom de la colonne utilisée pour dénombrer le nombre d'entités réalisant la commande (au choix : "finess","finessEtablissement" ou "rpps")

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

NB : dans la nouvelle version, les fichiers cibles sont restructurées selon la section 'adjust_fichier' du fichier de configuration.

#### Consolidation et publication au sftp

Consolider les fichiers et publier le fichier consolidé sur le serveur sftp :
```
python main.py tout consolide_publie --verbose True
```
Le fichier consolidé est transféré dans le dossier "fichiers_consolidés_" du répertoire /commandes_officines sur le serveur SFTP. Publie également une synthese du fichier sur le serveur SFTP.

Pour uniquement consolider les fichiers sans les publier :
```
python main.py tout consolide --verbose True
```

NB : le paramètre 'domaine' doit être obligatoirement renseigné à 'tout'

Attention : cette commande ne déclenche pas d'envoi de mail

#### Tout traiter 

Importer, transformer et consolider tous les fichiers puis publier le fichier consolidé sur le serveur sftp :
```
python main.py tout tout --verbose True
```
Le fichier consolidé est transféré dans le dossier "fichiers cible" du répertoire /commandes_officines sur le serveur SFTP.

Attention : cette commande ne déclenche pas d'envoi de mail

#### Envoi mail

Envoie le contenu du html généré lors de la consolidation des fichiers. Les destinataires et la messagerie d'envoi du mail sont configurés via le fichier de configuration.
```
python main.py tout envoi_mail --verbose True
```
NB  * : le paramètre 'domaine' doit être obligatoirement renseigné à 'tout'
NB ** : le serveur SMTP utilisé doit toléré une authentification SSL simple.

#### Nettoyer

Nettoie le répertoire local et les fichiers stockés en local :
```
python main.py tout nettoyer --verbose True
```
NB : le paramètre 'domaine' doit être obligatoirement renseigné à 'tout'


### Mise en forme des fichiers avec transform.py

Le fichier transform.py se trouve dans le dossier modules/transform. Il effectue une mise en forme des fichiers en 3 étapes :

- Ajustement : Renomme les colonnes si nécessaire et/ou ajoute les colonnes manquantes
- Pivot : Fait pivoter de colonne à ligne les commandes de vaccin
- Mise en forme : Remplit la colonne 'typePS', crée puis remplit les colonnes 'vaccin' et 'rangVaccinalPrevu' 
