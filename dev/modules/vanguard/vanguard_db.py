import sqlite3
import os
from .vanguard_dataclasses import *

vanguardDatabasePath = os.path.join(os.path.dirname(__file__), "databases/vanguard.db")

def vanguardCreateTables():
	connection = sqlite3.connect(vanguardDatabasePath)
	cursor = connection.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS players (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL,
			user_id INTEGER UNIQUE NOT NULL,
			character_id INTEGER,
			FOREIGN KEY(character_id) REFERENCES Character(id)
		)
	''')

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS Attributes (
			id INTEGER PRIMARY KEY,
			strength INTEGER,
			finesse INTEGER,
			vitality INTEGER,
			spellcasting INTEGER,
			speed INTEGER
		);
	''')

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS Character (
			id INTEGER PRIMARY KEY,
			name TEXT,
			level INTEGER,
			exp INTEGER,
			attributes_id INTEGER,
			FOREIGN KEY(attributes_id) REFERENCES Attributes(id)
		);
	''')

	connection.commit()
	connection.close()

def vanguardInitDatabase():
	vanguardCreateTables()

def vanguardInsertCharacterAttributes(attributes: Attributes) -> int:
	conn = sqlite3.connect(vanguardDatabasePath)
	cursor = conn.cursor()

	cursor.execute('''
		INSERT INTO Attributes (strength, finesse, vitality, spellcasting, speed)
		VALUES (?, ?, ?, ?, ?)
	''', (attributes.strength, attributes.finesse, attributes.vitality, attributes.spellcasting, attributes.speed))

	attributesID = cursor.lastrowid

	conn.commit()
	conn.close()

	return attributesID

def vanguardInsertCharacter(character: Character) -> int:
	conn = sqlite3.connect(vanguardDatabasePath)
	cursor = conn.cursor()

	attributesID = vanguardInsertCharacterAttributes(character.attributes)

	cursor.execute('''
		INSERT INTO Character (name, level, exp, attributes_id)
		VALUES (?, ?, ?, ?)
	''', (character.name, character.level, character.exp, attributesID))

	characterID = cursor.lastrowid

	conn.commit()
	conn.close()

	return characterID

def vanguardInsertPlayer(player: Player):
	conn = sqlite3.connect(vanguardDatabasePath)
	cursor = conn.cursor()

	characterID = vanguardInsertCharacter(player.character)

	cursor.execute('''
		INSERT OR REPLACE INTO players (username, user_id, character_id)
		VALUES (?, ?, ?)
	''', (player.username, player.ID, characterID))

	conn.commit()
	conn.close()

def vanguardGetPlayer(userID: int) -> Player:
	conn = sqlite3.connect(vanguardDatabasePath)
	cursor = conn.cursor()

	# Perform a JOIN to retrieve player, character, and attributes
	cursor.execute('''
		SELECT p.username, p.user_id, c.name, c.level, c.exp, a.strength, a.finesse, a.vitality, a.spellcasting, a.speed
		FROM players p
		JOIN Character c ON p.character_id = c.id
		JOIN Attributes a ON c.attributes_id = a.id
		WHERE p.user_id = ?
	''', (userID,))

	row = cursor.fetchone()

	if row:
		username, userID, character_name, level, exp, strength, finesse, vitality, spellcasting, speed = row
		attributes = Attributes(strength=strength, finesse=finesse, vitality=vitality, spellcasting=spellcasting, speed=speed)
		character = Character(name=character_name, level=level, exp=exp, attributes=attributes)
		player = Player(username=username, ID=userID, character=character)
		return player
	else:
		return None


def vanguardPlayerExists(userID: int) -> bool:
	conn = sqlite3.connect(vanguardDatabasePath)
	cursor = conn.cursor()
	cursor.execute('SELECT COUNT(*) FROM players WHERE user_id = ?', (userID,))
	count = cursor.fetchone()[0]
	conn.close()
	return count > 0