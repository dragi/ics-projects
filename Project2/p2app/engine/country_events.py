import sqlite3
from p2app.events.app import *
from p2app.events.countries import *

def initiate_country_search(connection, event):
    code = event.country_code()
    name = event.name()

    conditions = []
    params = []

    if code:
        conditions.append('country_code = ?')
        params.append(code)
    if name:
        conditions.append('name = ?')
        params.append(name)
    if conditions:
        where = ' AND '.join(conditions)
        query = f'SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE {where};'
    else:
        query = 'SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country;'

    cursor = connection.execute(query, params)

    rows = cursor.fetchall()
    for row in rows:
        yield CountrySearchResultEvent(Country(row[0], row[1], row[2], row[3], row[4], row[5]))

def load_country(connection, event):
    ident = event.country_id()
    cursor = connection.execute(
        'SELECT country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE country_id = :id;',
        {'id': ident})
    row = cursor.fetchone()

    if row:
        yield CountryLoadedEvent(Country(ident, row[0], row[1], row[2], row[3], row[4]))
    else:
        yield ErrorEvent('Country not found')

def save_country(connection, event):
    country = event.country()
    ident = country.country_id
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
    except sqlite3.IntegrityError as e:
        error_msg = str(e).upper()
        if 'FOREIGN KEY' in error_msg:
            yield SaveCountryFailedEvent('Invalid continent - please select a valid continent')
        elif 'UNIQUE' in error_msg or 'country_code' in error_msg:
            yield SaveCountryFailedEvent('A country with this code already exists')
        elif 'PRIMARY KEY' in error_msg:
            yield SaveCountryFailedEvent('A country with this ID already exists')
        elif 'NOT NULL' in error_msg:
            yield SaveCountryFailedEvent('Country code, name, continent, and wikipedia link are required')
        else:
            yield SaveCountryFailedEvent('Database error: unable to save country')
    except Exception:
        yield SaveCountryFailedEvent('Unable to save country')

def modify_country(connection, event):
    country = event.country()
    ident = country.country_id
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
    except sqlite3.IntegrityError as e:
        error_msg = str(e).upper()
        if 'FOREIGN KEY' in error_msg:
            yield SaveCountryFailedEvent('Invalid continent - please select a valid continent')
        elif 'UNIQUE' in error_msg or 'country_code' in error_msg:
            yield SaveCountryFailedEvent('Another country already uses this code')
        elif 'NOT NULL' in error_msg:
            yield SaveCountryFailedEvent('Country code, name, continent, and wikipedia link are required')
        else:
            yield SaveCountryFailedEvent('Database error: unable to update country')
    except Exception:
        yield SaveCountryFailedEvent('Unable to update country')