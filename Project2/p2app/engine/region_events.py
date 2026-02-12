import sqlite3
from p2app.events.app import *
from p2app.events.regions import *

def initiate_region_search(connection, event):
    code = event.region_code()
    name = event.name()
    local = event.local_code()
    cursor = connection.execute(
        'SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_code = :code;',
        {'code': code})
    rows = cursor.fetchall()
    for row in rows:
        yield RegionSearchResultEvent(Region(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

def load_region(connection, event):
    ident = event.region_id()
    cursor = connection.execute(
        'SELECT region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_id = :id;',
        {'id': ident})
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            yield RegionLoadedEvent(Region(ident, row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
    else:
        yield ErrorEvent('Region not found')

def save_region(connection, event):
    ident, code, local, name, cont, country, wiki, key = event.region()

    try:
        connection.execute(
            'INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
            (ident, code, local, name, cont, country, wiki, key))
        connection.commit()
        yield RegionSavedEvent(event.region())
    except sqlite3.IntegrityError:
        yield SaveRegionFailedEvent('This region already exists in the database')
    except Exception:
        yield SaveRegionFailedEvent('Unable to save region')


def modify_region(connection, event):
    region = event.region()
    ident, code, local, name, cont, country, wiki, key = region

    try:
        cursor = connection.execute(
            'UPDATE region SET region_code = ?, local_code = ?, name = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? WHERE region_id = ?;',
            (code, local, name, cont, country, wiki, key, ident))
        connection.commit()

        if cursor.rowcount > 0:
            yield RegionSavedEvent(region)
        else:
            yield SaveRegionFailedEvent('Region not found')
    except sqlite3.IntegrityError:
        yield SaveRegionFailedEvent('This region code already exists')
    except Exception:
        yield SaveRegionFailedEvent('Unable to update region')