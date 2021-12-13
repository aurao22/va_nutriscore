# Nutriscore by Vincent PREVOT and Aurélie RAOUL

Ce projet a été construit tel que :
* nettoyage et traitement des données dissociées des analyses
* analyse spécifique aux pays
* analyse spécifique des données nutritionnelles et des catégories de produit

## Ordre des traitements :
1. nutriscore_pre_traitement-VX.XX.ipynb : pour générer les fichiers de données propres
1. nutriscore_countries_analysis-VX.XX.ipynb : pour l'analyse de la partie pays
1. nutriscore_data_analysis-VX.XX.ipynb

## Pré-traitement :

Le pré-traitement des données consiste à charger le fichier de données sources, le compléter et le nettoyer, mais aussi, pré-calculer certaines informations pour alléger les fichiers des étapes d'analyse.

Dépendances interne au projet :

* nutriscore_pre_traitement-VX.XX.ipynb :
   * va_geo_nutriscore.py => traitements lié à la géo spécifique nutriscore
   * va_geo.py            => traitements lié à la géo non spécifique
   * nutriscore_pre_traitement.py => traitement des données
   * nutriscore_data_analysis.py => aspect graphique nécessaire aux analyses et représentations

Il faut donc lancer les pré traitement en premier avec les fichiers de données d'origine : data_nutriscore.csv de 4 529 026 Ko
Ce pré-traitement génère 2 fichiers :
* nutriscore_filtered_countries_<timestamp>.csv
  * Pour les pays, en plus du nettoyage / correction des données, un complément des données est effectué via 2 modules geo et un pré-calcul pour simplifier les étapes suivantes
* nutriscore_cleans_datas_<timestamp>.csv
  * Pour cette partie, l'essentiel du traitement consiste à corriger, nettoyer les données et de générer une version allégée du fichier de données d'origine


## Analyse des pays

L'analyse des pays prend en entrée le fichier nutriscore_filtered_countries_<timestamp>.csv généré par le pré-traitement

Dépendances interne au projet :

* nutriscore_countries_analysis-VX.XX.ipynb :
   * aucune dépendance spécifique au projet

## Analyse des données nutritionnelles et produits

Cette partie prend en entrée le fichier nutriscore_cleans_datas_<timestamp>.csv généré par le pré-traitement

Dépendances interne au projet :
* nutriscore_data_analysis-VX.XX.ipynb
   * nutriscore_pre_traitement.py => traitement des données
   * nutriscore_data_analysis.py => aspect graphique nécessaire aux analyses et représentations