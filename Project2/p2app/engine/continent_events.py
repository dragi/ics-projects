import sqlite3
from p2app.events.app import *
from p2app.events.continents import *

def initiate_search(connection, event):
    code = event.continent_code()
    name = event.name()
    cursor = connection.execute(
        'SELECT continent_id FROM continent WHERE continent_code = :code;',
        {'code': code})
    ids = cursor.fetchall()
    for ident in ids:
        yield ContinentSearchResultEvent(Continent(ident[0], code, name))

def load_continent(connection, event):
    ident = event.continent_id()
    cursor = connection.execute(
        'SELECT continent_code, name FROM continent WHERE continent_id = :id;',
        {'id': ident})
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            code, name = row
            yield ContinentLoadedEvent(Continent(ident, code, name))
    else:
        yield ErrorEvent('Continent not found')

def save_continent(connection, event):
    ident, code, name = event.continent()

    try:
        connection.execute(
            'INSERT INTO continent (continent_id, continent_code, name) VALUES (?, ?, ?);',
            (ident, code, name))
        connection.commit()
        yield ContinentSavedEvent(event.continent())
    except sqlite3.IntegrityError:
        yield SaveContinentFailedEvent('This continent already exists in the database')
    except Exception:
        yield SaveContinentFailedEvent('Unable to save continent')


def modify_continent(connection, event):
    continent = event.continent()
    ident = continent.continent_id
    code = continent.continent_code
    name = continent.name

    try:
        cursor = connection.execute(
            'UPDATE continent SET continent_code = ?, name = ? WHERE continent_id = ?;',
            (code, name, ident))
        connection.commit()

        if cursor.rowcount > 0:
            yield ContinentSavedEvent(continent)
        else:
            yield SaveContinentFailedEvent('Continent not found')
    except sqlite3.IntegrityError:
        yield SaveContinentFailedEvent('This continent code already exists')
    except Exception:
        yield SaveContinentFailedEvent('Unable to update continent')