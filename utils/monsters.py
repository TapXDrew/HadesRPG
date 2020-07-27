import random
import utils.weapons


class BadMonsterSelection(Exception):
    """Raised when an invalid monster type is selected or you are trying to attack an instance of the BaseMonster class"""


class BaseMonster:
    def __init__(self, name=None, location=None, level=None, health=None, armor=None, ws1=None, ws2=None, magic=None, manna=None, abilities=None, perks=None, power=None, speed=None, knowledge=None):
        self.number = None
        self.last_cords = None
        self.target = None
        self.can_pass_over = None

        self.name = name
        self.location = location
        self.level = level
        self.health = health
        self.armor = armor
        self.weapon_slot_one = ws1
        self.weapon_slot_two = ws2
        self.magic = magic
        self.manna = manna
        self.abilities = abilities
        self.perks = perks
        self.power = power
        self.speed = speed
        self.knowledge = knowledge
        self.image = None

    def attack(self, *args, **kwargs):
        raise BadMonsterSelection("Cannot attack an instance of the base monster class")


class Banshee(BaseMonster):
    def __init__(self, name, location, level, health, armor, ws1, ws2, magic, manna, abilities, perks, power, speed, knowledge):
        super().__init__(name, location, level, health, armor, ws1, ws2, magic, manna, abilities, perks, power, speed, knowledge)

    def attack(self, player):
        """"""


class Ghost(BaseMonster):
    def __init__(self, location, level=5, power=12, speed=1, name="Ghost", health=10, armor=0, magic=utils.weapons.air(1)):
        super().__init__(name=name, location=location, level=level, power=power, speed=speed, health=health, armor=armor, magic=magic)
        self.image = 'images/monsters/ghost.png'
        self.number = 9
        self.can_pass_over = [5]

    def attack(self, character):
        return self.magic.attack(self, character), self.magic.name
