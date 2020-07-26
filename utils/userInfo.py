import os
import sqlite3
import utils.characters
from utils.weapons import *

DATABASE = os.getcwd()+'/databases/PlayerData.db'
TABLE = 'Users'


class BadCharacter(Exception):
    pass


class BadCharacterColumn(Exception):
    pass


class User:
    def __init__(self, bot, ctx, user=None):
        self.bot = bot
        self.ctx = ctx
        self.user = user if user else ctx.author

        self.conn = None
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()

        self._create_table()
        self._get_user_info()

    def _create_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {TABLE} (id BIGINT PRIMARY KEY, character_1 TEXT, character_2 TEXT, character_3 TEXT, active_character TEXT)"""
        self.cursor.execute(query)
        self.conn.commit()

    def _create_user(self):
        try:
            query = f"""INSERT INTO {TABLE} VALUES (?, ?, ?, ?, ?)"""
            self.cursor.execute(query, (self.user.id, None, None, None, None))
            self.conn.commit()
        except sqlite3.Error:
            pass

    def _get_user_info(self):
        query = f"SELECT * FROM {TABLE} WHERE id = ?"
        self.cursor.execute(query, (self.user.id,))
        info = self.cursor.fetchall()
        if info:
            self.id = info[0][0]
            self.character_1 = info[0][1]
            self.character_2 = info[0][2]
            self.character_3 = info[0][3]
            self.active_character = info[0][4]
        else:
            self._create_user()
            self._get_user_info()

    def update_value(self, column, value):
        query = f"UPDATE {TABLE} set {column} = ? WHERE id = ?"
        self.cursor.execute(query, (value, self.user.id))
        self.conn.commit()
        self._get_user_info()

    def create_character(self, character_type, info_dump):
        if character_type == "Demon":
            character = utils.characters.Demon(info_dump)
        elif character_type == "Angel":
            character = utils.characters.Angel(info_dump)
        else:
            raise BadCharacter("Invalid character selection while creating a character")
        if not self.character_1:
            column = 'character_1'

        elif not self.character_2:
            column = 'character_2'

        elif not self.character_3:
            column = 'character_3'

        else:
            raise BadCharacterColumn("Invalid character column selected during character creation")

        self.update_value(column, character.char_dump)
