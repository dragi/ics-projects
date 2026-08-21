import sqlite3
from p2app.events.app import *
from p2app.events.continents import *

def initiate_continent_search(connection: sqlite3.Connection, event: StartContinentSearchEvent):
    """Search for continents matching the given criteria."""
    code = event.continent_code()
    name = event.name()
    conditions = []
    params = []

    if code:
        conditions.append('continent_code = ?')
        params.append(code)
    if name:
        conditions.append('name = ?')
        params.append(name)
    if conditions:
        where = ' AND '.join(conditions)
        query = f'SELECT continent_id, continent_code, name FROM continent WHERE {where};'
    else:
        query = 'SELECT continent_id, continent_code, name FROM continent;'

    cursor = connection.execute(query, params)
    rows = cursor.fetchall()

    for row in rows:
        yield ContinentSearchResultEvent(Continent(row[0], row[1], row[2]))

def load_continent(connection: sqlite3.Connection, event: LoadContinentEvent):
    """Load a continent by ID."""
    ident = event.continent_id()
    cursor = connection.execute(
        'SELECT continent_code, name FROM continent WHERE continent_id = :id;',
        {'id': ident})
    row = cursor.fetchone()

    if row:
        code, name = row
        yield ContinentLoadedEvent(Continent(ident, code, name))
    else:
        yield ErrorEvent('Continent not found')

def save_continent(connection: sqlite3.Connection, event: SaveNewContinentEvent):
    """Insert a new continent into the database."""
    continent = event.continent()
    ident = continent.continent_id
    code = continent.continent_code if continent.continent_code else None
    name = continent.name if continent.name else None

    try:
        connection.execute(
            'INSERT INTO continent (continent_id, continent_code, name) VALUES (?, ?, ?);',
            (ident, code, name))
        connection.commit()
        yield ContinentSavedEvent(event.continent())
    except sqlite3.IntegrityError as e:
        error_msg = str(e).upper()
        if 'UNIQUE' in error_msg or 'continent_code' in error_msg:
            yield SaveContinentFailedEvent('A continent with this code already exists')
        elif 'PRIMARY KEY' in error_msg:
            yield SaveContinentFailedEvent('A continent with this ID already exists')
        elif 'NOT NULL' in error_msg:
            yield SaveContinentFailedEvent('Continent code and name are required')
        else:
            yield SaveContinentFailedEvent('Database error: unable to save continent')
    except Exception:
        yield SaveContinentFailedEvent('Unable to save continent')

def modify_continent(connection: sqlite3.Connection, event: SaveContinentEvent):
    """Update an existing continent in the database."""
    continent = event.continent()
    ident = continent.continent_id
    code = continent.continent_code if continent.continent_code else None
    name = continent.name if continent.name else None

    try:
        cursor = connection.execute(
            'UPDATE continent SET continent_code = ?, name = ? WHERE continent_id = ?;',
            (code, name, ident))
        connection.commit()

        if cursor.rowcount > 0:
            yield ContinentSavedEvent(continent)
        else:
            yield SaveContinentFailedEvent('Continent not found')
    except sqlite3.IntegrityError as e:
        error_msg = str(e).upper()
        if 'UNIQUE' in error_msg or 'continent_code' in error_msg:
            yield SaveContinentFailedEvent('Another continent already uses this code')
        elif 'NOT NULL' in error_msg:
            yield SaveContinentFailedEvent('Continent code and name are required')
        else:
            yield SaveContinentFailedEvent('Database error: unable to update continent')
    except Exception:
        yield SaveContinentFailedEvent('Unable to update continent')