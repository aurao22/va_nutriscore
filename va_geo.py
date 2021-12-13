import numpy as np
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2, country_name_to_country_alpha3
from geopy.geocoders import Nominatim
from time import time
import pycountry

# ---------------------------------------------------------------------------------------------
#                               TRAITEMENT GEO
# ---------------------------------------------------------------------------------------------
# Variables globales
# ---------------------------------------------------------------------------------------------
# Correction des pays qui sont en erreur dans la librairie
lat_long = {('IT', 'EU'): (41.871940, 12.567380),  # Italie
            ('JP', 'AS'): (34.886306, 134.379711),  # ('JP', 'AS') Japan nan
            ('CZ', 'EU'): (49.817492, 15.472962),  # ('CZ', 'EU') Czech Republic nan
            ('VE', 'SA'): (6.423750, -66.589730),  # ('VE', 'SA') Venezuela nan
            ('NP', 'AS'): (28.394857, 84.124008),  # ('NP', 'AS') Nepal nan
            ('SY', 'AS'): (34.802075, 38.996815),  # ('SY', 'AS') Syria nan
            ('IE', 'EU'): (53.412910, -8.243890),  # ('IE', 'EU') Ireland nan
            ('UY', 'SA'): (-32.522779, -55.765835),  # ('UY', 'SA') Uruguay nan
            ('KY', 'NA'): (19.313300, -81.254600),  # ('KY', 'NA') Cayman Islands nan
            ('JO', 'AS'): (30.585164, 36.238414),  # ('JO', 'AS') Jordan nan
            ('ZW', 'AF'): (-19.015438, 29.154857),  # ('ZW', 'AF') Zimbabwe nan
            ('FI', 'EU'): (61.924110, 25.748151),  # ('FI', 'EU') Finland nan
            ('MW', 'AF'): (-13.254308, 34.301525),  # ('MW', 'AF') Malawi nan
            ('PY', 'SA'): (-23.442503, -58.443832),  # ('PY', 'SA') Paraguay nan
            ('UA', 'EU'): (44.874119, 33.151245),  # ('UA', 'EU') Ukraine nan
            ('EC', 'SA'): (-1.831239, -78.183406),  # ('EC', 'SA') Ecuador nan
            ('AM', 'AS'): (40.069099, 45.038189),  # ('AM', 'AS') Armenia nan
            ('LK', 'AS'): (7.873592, 80.773137),  # ('LK', 'AS') Sri Lanka nan
            ('PR', 'NA'): (18.220833, -66.590149),  # Puerto Rico
            ('GB', 'EU'): (52.3555177, -1.1743197),  # United Kingdom
            ('UG', 'AF'): (1.373333, 32.290275),  # ('UG', 'AF') Uganda nan
            ('GF', 'SA'): (3.921724136000023, -53.23312207499998),  # ('GF', 'SA') French Guiana nan
            ('PF', 'OC'): (-17.67739793399994, -149.40097329699998),  # French Polynesia nan
            ('GD', 'NA'): (12.151965053000026, -61.659644958999934),  # Grenada
            ('GY', 'SA'): (4.796422680000035, -58.97538657499996),  # Guyana
            ('JE', 'EU'): (49.21402591200007, -2.1327190749999545),  # Jersey
            ('MD', 'EU'): (47.20102827100004, 28.46370618900005),  # Moldova
            ('PW', 'OC'): (7.421479662000024, 134.511600068),  # Palau
            ('MF', 'NA'): (18.080477531000042, -63.06021562199999),  # Saint Martin
            ('SR', 'SA'): (3.9317774090000626, -56.01360780899995),  # Suriname
            ('VU', 'OC'): (-15.241355872999975, 166.8727570740001),  # Vanuatu
            ('AG', 'NA'): (17.0869391, -61.783491),
            ('BA', 'EU'): (43.9165389, 17.6721508),
            ('NL', 'NA'): (12.201890, -68.262383),
            ('CI', 'AF'): (7.5455112, -5.547545),  # Ivory Coast
            ('CW', 'NA'): (12.2135221, -68.9495816),
            ('CD', 'AF'): (-4.0335162, 21.7500603),
            ('FR', 'EU'): (46.71109, 1.7191036),
            ('IM', 'EU'): (54.2312716, -4.569504),
            ('MK', 'EU'): (41.6137143, 1.743258),  # North Macedonia
            ('RE', 'AF'): (-21.1306889, 55.5264794),
            ('TT', 'NA'): (10.4437128, -61.4191414),
            ('VI', 'NA'): (18.3434415, -64.8671634),
            ('BB', 'NA'): (13.1901325, -59.5355639),  # Barbados
            ('AW', 'NA'): (12.517572, -69.9649462),  # Aruba ('AW', 'NA') (nan, nan)
            ('GG', 'EU'): (49.4630653, -2.5881123),  # Guernesey
            ('PS', 'AS'): (31.947351, 35.227163),  # State of Palestine
            ("KN", "NA"): (17.2561791, -62.7019638),  # Saint Kitts and Nevis
            ("PM", "NA"): (46.9466881, -56.2622848),  # "Saint Pierre and Miquelon"
            ('VC', 'NA'): (13.252818, -61.197096),  # Saint Vincent And The Grenadines
            ('SX', 'NA'): (18.0347188, -63.0681114),  # Sint Maarten
            ('TT', 'SA'): (10.536421,-61.311951)      # 'Trinidad And Tobago'
            }

countries_dict = {}

# ---------------------------------------------------------------------------------------------
#                          Functions pour les données géographiques
# ---------------------------------------------------------------------------------------------

dic_country_code = {"Antigua and Barbuda": ("AG", 'NA'),  # "SA"
                    "Antigua And Barbuda": ("AG", 'NA'),  # "SA"
                    "Bosnia And Herzegovina": ("BA", "EU"),
                    "Caribbean Netherlands": ("NL", "NA"),
                    "Cote D Ivoire": ("CI", "AF"),
                    "Curacao": ("CW", "NA"),
                    'United Kingdom': ('GB', 'EU'),
                    'Democratic Republic Of The Congo': ("CD", "AF"),
                    'European Union': ('FR', 'EU'),
                    'Isle Of Man': ('IM', 'EU'),
                    'Republic Of Macedonia': ('MK', 'EU'),
                    'North Macedonia': ('MK', 'EU'),
                    'Reunion': ('RE', 'AF'),
                    'Trinidad And Tobago': ('TT', 'NA'),
                    'Virgin Islands Of The United States': ('VI', 'NA'),
                    "Saint Kitts And Nevis": ("KN", "NA"),
                    "Saint Pierre And Miquelon": ("PM", "NA"),
                    "Sint Maarten": ("SX", "NA"),
                    "State of Palestine": ('PS', 'AS'),
                    'Trinidad And Tobago':('TT', 'SA'),
                    'Dominican Republic':('DO', 'SA')
                    }


# 1. Conversion to Alpha 2 codes and Continents
def get_continent(country_name_param, include_format=False, verbose=False):
    """
    :param country_name_param (str): nom du pays recherché en anglais, attention, doit avoir des majuscules aux premières lettre de chaque mot, mais pas sur les petits mot
    :param include_format (boolean): True pour lancer le formatage (majuscules aux 1ère lettre et pas pour les petits mots du type : of,and, ...)
    :param verbose (boolean): True pour mode debug
    :return: (str, str) :(country a2 code, continent code)
    """
    country_name = country_name_param
    cn_a2_code = np.nan
    cn_a3_code = np.nan
    cn_continent = np.nan
    if country_name is not None and len(country_name) > 0:
        if include_format:
            country_name = country_name.title()
            country_name = country_name.replace(" Of ", " of ")
            country_name = country_name.replace(" The ", " the ")
            country_name = country_name.replace(" And ", " and ")
        try:
            cn_a2_code = country_name_to_country_alpha2(country_name)
        except:
            cn_a2_code = dic_country_code.get(country_name, np.nan)
            if cn_a2_code != np.nan:
                try:
                    cn_a2_code = cn_a2_code[0]
                except:
                    if verbose:
                        print("cn_a2_code ",country_name, "=> FAIL : ", cn_a2_code)
                    cn_a2_code = np.nan
        try:
            cn_a3_code = country_name_to_country_alpha3(country_name)
        except:
            if verbose:
                print("cn_a3_code ",country_name, "=> FAIL alpha3 : ", cn_a3_code)
            cn_a3_code = np.nan

        try:
            cn_continent = country_alpha2_to_continent_code(cn_a2_code)
        except:
            cn_continent = dic_country_code.get(country_name, np.nan)
            if cn_continent != np.nan:
                cn_continent = cn_continent[1]
    return cn_a2_code, cn_continent, cn_a3_code


def get_geolocation(country, geolocator=None, verbose=False):
    """
    :param country :(str, str)(country a2 code, continent code)
    :param geolocator: Nominatim
    :param verbose (boolean): True pour mode debug
    :return:(float, float):(latitude, longitude) or (nan, nan)
    """
    if geolocator is None:
        geolocator = Nominatim(user_agent="catuserbot")
    try:
        if country in lat_long.keys():
            return lat_long.get(country, np.nan)
        else:
            # Geolocate the center of the country
            loc = geolocator.geocode(country)
            # And return latitude and longitude
            return loc.latitude, loc.longitude
    except:
        # Return missing value
        return np.nan, np.nan
   

def get_country_alpha3(country_name, alpha2, verbose=False):
    alpha3 = None

    if alpha2 is not None:
        try:
            pcountry = pycountry.countries.get(alpha_2=alpha2)
            if pcountry is not None:
                alpha3 = pcountry.alpha_3
        except:
            pass
    # On essaie avec le nom
    if country_name is not None and country_name is None:
        alpha3 = __get_country_alpha3_with_name(country_name, verbose)

    if alpha3 is None and verbose:
        print("cn_a3_code FAIL => ", country_name, alpha2)
    return alpha3


def get_country_official_name(country_name, alpha2, alpha3, verbose=False):
    official_name = None
    if alpha2 is not None:
        official_name = __get_country_official_name_with_alpha2(alpha2, verbose)
    
    if official_name is None and country_name is not None:
        official_name = __get_country_official_name_with_name(country_name, verbose)

    if official_name is None and alpha3 is not None:
        official_name = __get_country_official_name_with_alpha3(alpha3, verbose)

    return official_name


# ---------------------------------------------------------------------------------------------
#                               Préparation des données
# ---------------------------------------------------------------------------------------------
def get_country_data(country_name_param, geolocator=None, include_format=False, verbose=False):
    """
    Récupère les données du pays
    :param country_name_param (str): nom du pays recherché en anglais, attention, doit avoir des majuscules aux premières lettre de chaque mot, mais pas sur les petits mot
    :param geolocator: Nominatim
    :param include_format (boolean): True pour lancer le formatage (majuscules aux 1ère lettre et pas pour les petits mots du type : of,and, ...)
    :param verbose (boolean): True pour mode debug
    :return: (str, str, float, float) : country_code, continent_code, latitude, longitude
    """
    t0 = time()
    country_name = country_name_param
    country_code, continent_code, alpha3 = get_continent(country_name, include_format, verbose)
    latitude = np.nan
    longitude = np.nan

    if country_code != np.nan and continent_code != np.nan:
        if geolocator is None:
            geolocator = Nominatim(user_agent="catuserbot")

        geoloc = get_geolocation((country_code, continent_code), geolocator)
        if geoloc != np.nan:
            try:
                latitude = geoloc[0]
                longitude = geoloc[1]
            except TypeError:
                print("TypeError for :", (country_code, continent_code), country_name, geoloc)
        else:
            print("Country not found geoloc :", (country_code, continent_code), country_name)
    else:
        if country_name == 'Holy See':
            latitude = 41.902916
            longitude = 12.453389
        else:
            print("Country not known :", country_name)

    if alpha3 is None and (country_code is not None or country_name is not None) :
        alpha3 = get_country_alpha3(country_name, country_code)

    official_name = get_country_official_name(country_name, country_code, alpha3)
    
    t1 = time() - t0
    if verbose:
        print("get_country_data", country_name,
              " in {0:.3f} secondes................................................... END".format(t1))
    return country_code, continent_code, latitude, longitude, alpha3, official_name

# ---------------------------------------------------------------------------------------------
#                               MAIN
# ---------------------------------------------------------------------------------------------

def __get_country_alpha3_with_name(country_name, verbose=False):
    alpha3 = None
    if country_name is not None:
        # On essaie avec le nom
        try:
            pcountry = pycountry.countries.get(name=country_name)
            if pcountry is not None:
                if alpha3 is None:
                    alpha3 = pcountry.alpha_3
        except:
            pass
    if alpha3 is None and verbose:
        print("cn_a3_code FAIL => ", country_name)
    return alpha3

def __get_country_official_name_with_name(country_name, verbose=False):
    official_name = None
    if country_name is not None:
        # On essaie avec le nom
        try:
            pcountry = pycountry.countries.get(name=country_name)
            if pcountry is not None:
                if official_name is None:
                    official_name = pcountry.official_name
        except:
            pass
    if official_name is None and verbose:
        print("official_name FAIL => ", country_name)
    return official_name

def __get_country_official_name_with_alpha3(alpha3, verbose=False):
    official_name = None
    if alpha3 is not None:
        # On essaie avec le nom
        try:
            pcountry = pycountry.countries.get(alpha3=alpha3)
            if pcountry is not None:
                if official_name is None:
                    official_name = pcountry.official_name
        except:
            pass
    if official_name is None and verbose:
        print("official_name FAIL => ", alpha3)
    return official_name


def __get_country_official_name_with_alpha2(alpha2, verbose=False):
    official_name = None
    if alpha2 is not None:
        try:
            pcountry = pycountry.countries.get(alpha_2=alpha2)
            if pcountry is not None:
                official_name = pcountry.official_name
        except:
            pass
    if official_name is None and verbose:
        print("official_name FAIL => ", alpha2)

    return official_name

# ---------------------------------------------------------------------------------------------
#                               MAIN
# ---------------------------------------------------------------------------------------------
def main():
    pass


main()


# ---------------------------------------------------------------------------------------------
#                               TESTS
# ---------------------------------------------------------------------------------------------
def __test():
    pass
