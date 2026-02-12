import sqlite3
from p2app.events.app import *
from p2app.events.countries import *

def initiate_country_search(connection, event):
    code = event.country_code()
    name = event.name()
    cursor = connection.execute(
        'SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE country_code = :code;',
        {'code': code})
    rows = cursor.fetchall()
    for row in rows:
        yield CountrySearchResultEvent(Country(row[0], row[1], row[2], row[3], row[4], row[5]))

def load_country(connection, event):
    ident = event.country_id()
    cursor = connection.execute(
        'SELECT country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE country_id = :id;',
        {'id': ident})
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            yield CountryLoadedEvent(Country(ident, row[0], row[1], row[2], row[3], row[4]))
    else:
        yield ErrorEvent('Country not found')

def save_country(connection, event):
    country = event.country()
    ident = country.country_id()
    code = country.country_code if country.country_code else None
    name = country.name if country.name else None
    cont = country.continent_id
    wiki = country.wikipedia_link if country.wikipedia_link else None
    keywords = country.keywords if country.keywords else None

    try:
        connection.execute(
            'INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?);',
            (ident, code, name, cont, wiki, keywords))
        connection.commit()
        yield CountrySavedEvent(event.country())
    except sqlite3.IntegrityError:
        yield SaveCountryFailedEvent('This country already exists in the database')
    except Exception:
        yield SaveCountryFailedEvent('Unable to save country')


def modify_country(connection, event):
    country = event.country()
    ident = country.country_id()
    code = country.country_code if country.country_code else None
    name = country.name if country.name else None
    cont = country.continent_id
    wiki = country.wikipedia_link if country.wikipedia_link else None
    keywords = country.keywords if country.keywords else None

    try:
        cursor = connection.execute(
            'UPDATE country SET country_code = ?, name = ?, continent_id = ?, wikipedia_link = ?, keywords = ? WHERE country_id = ?;',
            (code, name, cont, wiki, keywords, ident))
        connection.commit()

        if cursor.rowcount > 0:
            yield CountrySavedEvent(event.country())
        else:
            yield SaveCountryFailedEvent('Country not found')
    except sqlite3.IntegrityError:
        yield SaveCountryFailedEvent('This country code already exists')
    except Exception:
        yield SaveCountryFailedEvent('Unable to update country')