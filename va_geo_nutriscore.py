import sys
# insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(1, '../modules')
import va_geo
import va_geo_nutriscore_constants as va_cons
import pandas as pd
import numpy as np
from time import time
import re

# ---------------------------------------------------------------------------------------------
#                               TRAITEMENT DES PAYS
# ---------------------------------------------------------------------------------------------

def split_country_columns(df, country_column_name='countries_tags', verbose=False):
    """
    Sépare les données de la colonne pays et ajoute autant de colonnes que nécessaire
    :param df: <Dataframe> : the dataframe, with the column with all countries name
    :param country_column_name:the column name with all countries name
    :param verbose: <boolean>: True pour mode debug
    :return: <Dataframe>: df_country
    """
    t0 = time()
    print("split_country_columns ", end="")

    # Séparation des code pays et des pays
    df_country = _split_country_columns(df, country_column_name, ",", verbose)
    print(df_country.shape[0],">", end="")
    df_country = _split_country_columns(df_country, "country", ":", verbose)
    print(df_country.shape[0],">", end="")
    df_country = _split_country_columns(df_country, "country", ", ", verbose)
    print(df_country.shape[0],">", end="")
    df_country.loc[ (df_country["country"]=="unknown") 
                    | (df_country["country"]=="bdbdb")
                    | (df_country["country"]=="10-07-21")
                    | (df_country["country"]=="1-53")
                    | (df_country["country"]=="4-3")
                    , "country"] = np.nan
    df_country.dropna(inplace=True)

    # Correction des noms qui resteraient
    for str in va_cons.str_to_remove_from_name:
        df_country["country"] = df_country["country"].str.replace(str.lower(), "")
    # Les suppressions de second niveau
    for str in va_cons.str_to_remove_second_step_from_name:
        df_country["country"] = df_country["country"].str.replace(str.lower(), "")
    # Il ne faut pas supprimer les tirets, sinon on ne retrouvera pas ce nom dans le calcul du nombre de pays
    #df_country["country"] = df_country["country"].str.replace("-", " ")
    
    df_country["country"] = df_country["country"].str.strip()

    # Suppression des doublons
    df_country = df_country.drop_duplicates("country", keep="first")
    df_country.sort_values("country")
        
    t1 = time() - t0
    print(df_country.shape[0],"in {0:.2f} secondes................................................... END".format(t1))
    return df_country


def _split_country_columns(df, country_column_name='countries_tags', separator=",", verbose=False):
    """
    Sépare les données de la colonne pays et ajoute autant de colonnes que nécessaire
    :param df: <Dataframe> : the dataframe, with the column with all countries name
    :param country_column_name:the column name with all countries name
    :param verbose: <boolean>: True pour mode debug
    :return: <Dataframe>: df_country, nombre de colonnes pays
    """
    # Séparation des code pays et des pays
    ser_count=pd.Series(", ".join(df[country_column_name].dropna()).split(separator))
    df_country = pd.DataFrame([ser_count])
    # On inverse le tableau car les pays étaients de colonne, pour les passer en ligne
    df_country = df_country.transpose()
    df_country = df_country.rename(columns={0: "country"})
    # On supprime les espaces qui sont restés suite au split
    df_country[ "country"] = df_country[ "country"].str.strip()
    # Suppression des doublons
    df_country = df_country.drop_duplicates("country", keep="first")
    # Suppression des pays avec un nom de taille inférieur à 4
    df_country.loc[(df_country["country"].str.len() < 4), "country"] = np.nan
    df_country.loc[(df_country["country"].str.len() > 100), "country"] = np.nan
    df_country.dropna(inplace=True)

    df_country.sort_values("country")
    
    return df_country


def get_official_country_name(origin_countries_names, verbose=False):
    """
    :param origin_countries_names: <Set> liste des noms de pays à nettoyer
    :param str_to_remove_from_name:correspondance_with_official_name
    :param correspondance_with_official_name:correspondance_with_official_name
    :param verbose: <boolean>: True pour mode debug
    :return: <dict<str:str>> : dictionnaire avec en clé le nom d'origine du pays et en valeur le nom du pays après nettoyage
    """
    t0 = time()
    print("clean_countries_names ", end="")
    if verbose:
        print("")
    countries_names_origin_to_new = {}

    correspondance_with_official_name = va_cons.data_country_names_their_official_name()

    for origin in origin_countries_names:

        origin = va_cons.clean_name(origin, False, False)
        name = va_cons.clean_name(origin, True, True)

        # Certaines valeurs doivent être supprimée
        if isinstance(name, str):
            name = correspondance_with_official_name.get(origin.lower(), name)
            countries_names_origin_to_new[origin] = name
            if verbose:
                print("'"+str(origin)+"'", ":", "'"+str(name)+"',")
            else:
                print(".", end="")
        
    t1 = (time() - t0) / 60
    print(len(countries_names_origin_to_new)," in {0:.2f} minutes................................. END".format(t1))
    return countries_names_origin_to_new


def get_boolean_series_for_country(country_name, country_name_origin, df, verbose=False):
    # TO_FIX traiter le warning ou comment traiter les données applicables au monde
    # UserWarning: This pattern has match groups. To actually get the groups, use str.extract.
    #   "(" + country_name_origin + "|all-over-the-world|world)"
    # cou[country_name_origin] = cou["countries_tags"].str.contains(
    #     "(" + country_name_origin + "|world)",
    #     regex=True)  # all-over-the-world
    official_name_to_origine = va_cons.official_country_name_their_data_variations(verbose=verbose)
    # Contruction du pattern avec toutes les variantes connues du nom du pays
    if country_name_origin is None:
        country_name_origin = country_name
    pattern = country_name_origin
    variant = official_name_to_origine.get(country_name, set())
    for name in variant:
        pattern = pattern + "|" + name
    # Séries indiquant si la ligne concerne le pays ou non
    boolean_series = df["countries_tags"].str.contains("(" + pattern + "|world|mundo)", regex=True)
    # Il faut remplacer les valeurs NA, sinon il n'est pas possible de faire une sélection ensuite
    boolean_series.fillna(value=False, inplace=True)
    return boolean_series


# ---------------------------------------------------------------------------------------------
#                          Functions pour les données géographiques
# ---------------------------------------------------------------------------------------------
def create_df_by_country_with_location(countries_names_origin_to_new, df, verbose, only=None):
    """
    :param countries_names_origin_to_new: <dict(str:str)> dictionnaire avec en clé le nom d'origine du pays (dans le df) et en valeur le nom officiel
    :param df:<Dataframe>
    :param verbose: <boolean>: True pour mode debug
    :return: <Dataframe> : Countries dataframe
    """
    t0 = time()
    dataframe_country_result = None
    ct_name = only
    if ct_name is None:
        ct_name = countries_names_origin_to_new.keys()
    nb_fail = 0
    # Il faut traiter tous les pays
    for country_name_origin in ct_name:
        country_name_clean = countries_names_origin_to_new[country_name_origin]
        
        boolean_series = get_boolean_series_for_country(country_name_clean, country_name_origin, df, verbose)

        # Réduction du nombre de lignes à celles du pays et ajout du nombre de lignes concernées pour ce pays
        df_country_alone_limit = df[boolean_series]
        df_country_alone_limit = df_country_alone_limit[['nutriscore_grade', 'nova_group', "pnns_groups_1", "pnns_groups_2", "pnns_groups"]]

        # Correction de l'index pour ajouter les informations du pays
        df_country_alone_limit = df_country_alone_limit.reset_index()
        if verbose:
            print(df_country_alone_limit.head(10))
            print(df_country_alone_limit.dtypes)
            print(df_country_alone_limit.shape, " <==> ", country_name_origin, country_name_clean)
        else:
            print(".", end="")

        # Ajout des informations pays
        country_code = np.nan
        continent_code = np.nan
        latitude = np.nan
        longitude = np.nan
        alpha3 = np.nan
        official_name = np.nan
        try:
            # On ajoute dans le dictionnaire les informations du pays
            country_code, continent_code, latitude, longitude, alpha3, official_name = va_geo.get_country_data(country_name_clean, verbose=verbose)
        except Exception as inst:
            # print(type(inst))    # the exception instance
            # print(inst.args)     # arguments stored in .args
            # print(inst)          # __str__ allows args to be printed directly,
            #                      # but may be overridden in exception subclasses
            # x, y = inst.args     # unpack args
            # print('x =', x)
            # print('y =', y)
            print("\n/!\\ FAIL :", country_name_origin, "<=>", country_name_clean, type(inst), inst.args, inst, "FAIL /!\\")
            nb_fail += 1

        # On ajoute dans le dictionnaire les informations du pays
        df_country_alone_limit["country_origin"] = country_name_origin
        df_country_alone_limit["country_clean"] = country_name_clean
        df_country_alone_limit["country_code"] = country_code
        df_country_alone_limit["continent_code"] = continent_code
        df_country_alone_limit["latitude"] = latitude
        df_country_alone_limit["longitude"] = longitude
        df_country_alone_limit["country_alpha3"] = alpha3
        if official_name is None:
            official_name = country_name_clean
        df_country_alone_limit["official_name"] = official_name
        if verbose:
             print(country_name_origin, country_code, continent_code, latitude, longitude, alpha3, official_name)
        # Coordinates - END
        if dataframe_country_result is None:
            dataframe_country_result = df_country_alone_limit
        else:
            # TODO ajouter le pays à la suite du df
            dataframe_country_result = dataframe_country_result.append(df_country_alone_limit, ignore_index=True)
    # Renomma de la colonne
    #dataframe_country_result.rename(columns={'0': 'country_count_values_by_cat'}, inplace=True)
    t1 = (time() - t0)/60
    print("\ncreate_df_by_country_with_location",nb_fail," FAILs in {0:.3f} minutes............................................ END".format(t1))
    return dataframe_country_result


# ---------------------------------------------------------------------------------------------
#                               TESTS
# ---------------------------------------------------------------------------------------------
def __test_pays(verbose=False):
    test_list = ['Argentina Espanol', 'Armenia Pyсский', 'Aruba Espanol', 'Australia English', 'Austria Deutsch',
                 'Azerbaijan Русский', 'Belarus Pyсский', 'Belgium Francais', 'Belgium Nederlands',
                 'Bolivia Espanol',
                 'Bosnia I Hercegovina Bosnian', 'Botswana English', 'Brazil Portugues', 'Bulgaria Български',
                 'Cambodia English',
                 'Cambodia ភាសាខ្មែរ', 'Canada English', 'Canada Francais', 'Chile Espanol', 'China 中文',
                 'Colombia Espanol',
                 'Costa Rica Espanol', 'Croatia Hrvatski', 'Cyprus Ελληνικά', 'Czech Republic Čeština',
                 'Denmark Dansk',
                 'Ecuador Espanol', 'El Salvador Espanol', 'Estonia Eesti', 'Europe', 'Fes', 'Finland Suomi',
                 'France Francais', 'Georgia ქართული', 'Germany Deutsch', 'Ghana English', 'Greece Ελληνικά',
                 'Guatemala Espanol',
                 'Honduras Espanol', 'Hong Kong 粵語', 'Hungary Magyar', 'Iceland Islenska', 'India English',
                 'Indonesia Bahasa Indonesia', 'Inglaterra', 'Ireland English', 'Israel עברית', 'Italy Italiano',
                 'Jamaica English', 'Japan 日本語', 'Kazakhstan Pyсский', 'Korea 한국어', 'Kyrgyzstan Русский',
                 'Latvia Latviešu', 'Lebanon English', 'Lesotho English', 'Lithuania Lietuvių', 'Macau 中文',
                 'Malaysia Bahasa Melayu', 'Malaysia English', 'Malaysia 中文', 'Maroc', 'Mexico Espanol',
                 'Middle East Africa',
                 'Moldova Roman', 'Mongolia Монгол Хэл', 'Mundo', 'Namibia English', 'Netherlands Nederlands',
                 'New Zealand English',
                 'Nicaragua Espanol', 'North Macedonia Македонски Јазик', 'Norway Norsk', 'Paises Bajos',
                 'Panama Espanol',
                 'Paraguay Espanol', 'Peru Espanol', 'Philippines', 'Poland Polski', 'Portugal Portugues',
                 'Puerto Rico Espanol',
                 'Republica Dominicana Espanol', 'Romania Romană', 'Russia Русский', 'Serbia Srpski',
                 'Singapore English',
                 'Slovak Republic Slovenčina', 'Slovenia Slovene', 'South Africa English', 'Spain Espanol', 'Suiza',
                 'Swaziland English', 'Sweden Svenska', 'Switzerland Deutsch', 'Switzerland Francais', 'Taiwan 中文',
                 'Thailand ไทย', 'Trinidad Tobago English', 'Turkey Turkce', 'U S Minor Outlying Islands',
                 'Ukraine Yкраї́Нська',
                 'United Kingdom English', 'United States English', 'United States Espanol', 'Uruguay Espanol',
                 'Venezuela Espanol',
                 'Vietnam Tiếng Việt', 'Zambia English', 'afghanistan', 'algeria', 'allemagne', 'american-samoa',
                 'andorra',
                 'angola', 'anguilla', 'antigua-and-barbuda', 'argentina', 'armenia', 'aruba', 'australia',
                 'austria', 'autriche',
                 'bahrain', 'bangladesh', 'barbados', 'belgique', 'belgium', 'bermuda', 'bolivia',
                 'bosnia-and-herzegovina',
                 'brazil', 'british-virgin-islands', 'bulgaria', 'burkina-faso', 'cambodia', 'cameroon', 'canada',
                 'caribbean-netherlands',
                 'chile', 'china', 'colombia', 'costa-rica', 'cote-d-ivoire', 'croatia', 'cuba', 'curacao',
                 'cyprus', 'czech-republic',
                 'democratic-republic-of-the-congo', 'denmark', 'deutschland', 'djibouti', 'dominican-republic',
                 'ecuador', 'egypt',
                 'el-salvador', 'en-en-united-kingdom', 'estados-unidos', 'etats-unis', 'ethiopia',
                 'european-union', 'finland', 'france',
                 'france-united-states', 'francia', 'frankreich', 'french-guiana', 'french-polynesia', 'gabon',
                 'georgia', 'germany',
                 'ghana', 'gibraltar', 'greece', 'grenada', 'guadeloupe', 'guam', 'guatemala', 'guernsey', 'guinea',
                 'guyana', 'haiti',
                 'honduras', 'hong-kong', 'hungary', 'iceland', 'india', 'indonesia', 'iran', 'iraq', 'ireland',
                 'isle-of-man', 'israel',
                 'italy', 'jamaica', 'japan', 'jersey', 'jordan', 'kazakhstan', 'kenya', 'kuwait', 'laos',
                 'lebanon', 'libya', 'luxembourg',
                 'malaysia', 'maldives', 'mali', 'martinique', 'mauritius', 'mayotte', 'mexico', 'moldova',
                 'monaco', 'mongolia', 'morocco',
                 'myanmar', 'netherlands', 'new-caledonia', 'new-zealand', 'nicaragua', 'niger',
                 'northern-mariana-islands', 'norway',
                 'oman', 'pakistan', 'palau', 'palestinian-territories', 'panama', 'paraguay', 'peru',
                 'philippines', 'poland', 'portugal',
                 'puerto-rico', 'qatar', 'republic-of-macedonia', 'republic-of-the-congo', 'reunion', 'romania',
                 'royaume-uni', 'russia',
                 'rwanda', 'saint-kitts-and-nevis', 'saint-lucia', 'saint-martin', 'saint-pierre-and-miquelon',
                 'saint-vincent-and-the-grenadines', 'san-marino', 'saudi-arabia', 'senegal', 'serbia',
                 'seychelles', 'sierra-leone',
                 'singapore', 'sint-maarten', 'slovakia', 'slovenia', 'somalia', 'south-africa', 'south-korea',
                 'spain', 'spanien',
                 'suriname', 'sweden', 'switzerland', 'taiwan', 'thailand', 'the-bahamas', 'togo',
                 'trinidad-and-tobago', 'tunisia',
                 'turkey', 'ukraine', 'united-arab-emirates', 'united-kingdom', 'united-states', 'uruguay',
                 'uzbekistan', 'vanuatu',
                 'venezuela', 'vietnam', 'virgin-islands-of-the-united-states', 'لأردن']

    

    
