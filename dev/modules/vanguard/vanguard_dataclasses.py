from dataclasses import dataclass, field
from typing import Dict, Any, Union

@dataclass
class Attributes:
	strength: int
	finesse: int
	vitality: int
	spellcasting: int
	speed: int

@dataclass
class Item:
	ID: int
	name: str
	type: str  # e.g., 'weapon', 'armor', 'consumable'
	description: str
	effects: Dict[str, int] = field(default_factory=dict)

	def use(self)-> Any:
		"""
		Method to use the item. This will be overridden in subclasses.
		Returns effects or None based on the item type.
		"""
		raise NotImplementedError("This method should be overridden in subclasses.")

@dataclass
class Archetype:
	name: str
	ID: int

@dataclass
class Essence:
	name: str
	ID: int

@dataclass
class Character:
	name: str
	level: int
	exp: int
	attributes: Attributes

@dataclass
class Player:
	username: str
	ID: int
	character: Character