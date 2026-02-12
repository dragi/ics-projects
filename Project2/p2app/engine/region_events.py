import sqlite3
from p2app.events.app import *
from p2app.events.regions import *

def initiate_region_search(connection, event):
    code = event.region_code()
    name = event.name()
    local = event.local_code()
    conditions = []
    params = []

    if code:
        conditions.append('region_code = ?')
        params.append(code)
    if name:
        conditions.append('name = ?')
        params.append(name)
    if local:
        conditions.append('local_code = ?')
        params.append(local)
    if conditions:
        where = ' AND '.join(conditions)
        query = f'SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE {where};'
    else:
        query = 'SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region;'

    cursor = connection.execute(query, params)
    rows = cursor.fetchall()

    for row in rows:
        yield RegionSearchResultEvent(Region(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

def load_region(connection, event):
    ident = event.region_id()
    cursor = connection.execute(
        'SELECT region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_id = :id;',
        {'id': ident})
    row = cursor.fetchone()

    if row:
        yield RegionLoadedEvent(Region(ident, row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
    else:
        yield ErrorEvent('Region not found')

def save_region(connection, event):
    region = event.region()
    ident = region.region_id
    code = region.region_code if region.region_code else None
    local = region.local_code if region.local_code else None
    name = region.name if region.name else None
    cont = region.continent_id
    country = region.country_id
    wiki = region.wikipedia_link if region.wikipedia_link else None
    key = region.keywords if region.keywords else None

    try:
        connection.execute(
            'INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
            (ident, code, local, name, cont, country, wiki, key))
        connection.commit()
        yield RegionSavedEvent(event.region())
    except sqlite3.IntegrityError as e:
        error_msg = str(e).upper()
        if 'FOREIGN KEY' in error_msg:
            yield SaveRegionFailedEvent('Invalid continent or country - please select valid values')
        elif 'UNIQUE' in error_msg or 'region_code' in error_msg:
            yield SaveRegionFailedEvent('A region with this code already exists')
        elif 'PRIMARY KEY' in error_msg:
            yield SaveRegionFailedEvent('A region with this ID already exists')
        elif 'NOT NULL' in error_msg:
            yield SaveRegionFailedEvent('Region code, local code, name, continent, and country are required')
        else:
            yield SaveRegionFailedEvent('Database error: unable to save region')
    except Exception:
        yield SaveRegionFailedEvent('Unable to save region')

def modify_region(connection, event):
    region = event.region()
    ident = region.region_id
    code = region.region_code if region.region_code else None
    local = region.local_code if region.local_code else None
    name = region.name if region.name else None
    cont = region.continent_id
    country = region.country_id
    wiki = region.wikipedia_link if region.wikipedia_link else None
    key = region.keywords if region.keywords else None

    try:
        cursor = connection.execute(
            'UPDATE region SET region_code = ?, local_code = ?, name = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? WHERE region_id = ?;',
            (code, local, name, cont, country, wiki, key, ident))
        connection.commit()

        if cursor.rowcount > 0:
            yield RegionSavedEvent(region)
        else:
            yield SaveRegionFailedEvent('Region not found')
    except sqlite3.IntegrityError as e:
        error_msg = str(e).upper()
        if 'FOREIGN KEY' in error_msg:
            yield SaveRegionFailedEvent('Invalid continent or country - please select valid values')
        elif 'UNIQUE' in error_msg or 'region_code' in error_msg:
            yield SaveRegionFailedEvent('Another region already uses this code')
        elif 'NOT NULL' in error_msg:
            yield SaveRegionFailedEvent('Region code, local code, name, continent, and country are required')
        else:
            yield SaveRegionFailedEvent('Database error: unable to update region')
    except Exception:
        yield SaveRegionFailedEvent('Unable to update region')