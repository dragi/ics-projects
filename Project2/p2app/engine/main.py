# p2app/engine/main.py
#
# ICS 33 Winter 2026
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.
from p2app.events import *
from p2app.engine.continent_events import *
import sqlite3


class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self._connection = None


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""
        if isinstance(event, OpenDatabaseEvent):
            yield from self.open_database(event)
        elif isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent
        elif isinstance(event, CloseDatabaseEvent):
            yield DatabaseClosedEvent
        elif isinstance(event, StartContinentSearchEvent):
            yield from initiate_search(self._connection, event)
        elif isinstance(event, LoadContinentEvent):
            yield from load_continent(self._connection, event)
        elif isinstance(event, SaveNewContinentEvent)
            yield from save_continent(self._connection, event)
        elif isinstance(event, SaveContinentEvent):
            yield from modify_continent(self._connection, event)


    def open_database(self, event):
        database_path = event.path()
        try:
            self._connection = sqlite3.connect(database_path)
            self._connection.execute('PRAGMA foreign_keys = ON;')
            cursor = self._connection.execute("SELECT * FROM airport WHERE airport_ident = 'KSNA';")
            if cursor.fetchone() is not None:
                yield p2app.events.DatabaseOpenedEvent(database_path)
            else:
                yield p2app.events.DatabaseOpenFailedEvent('The database failed to open successfully')
        except sqlite3.DatabaseError:
            yield p2app.events.DatabaseOpenFailedEvent('The database is invalid or corrupt')
        except Exception:
            yield p2app.events.DatabaseOpenFailedEvent('An unexpected error occurred')








