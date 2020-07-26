import math
import random


class Empty:
    """Empty weapon type; This is used as a place holder before the character has a weapon in the slot"""
    def __init__(self, *args, **kwargs):
        self.name = None

    def attack(self, *args, **kwargs):
        pass


class BaseSword:
    def __init__(self, element=None, aoe=False, aoe_type=None):
        """The base class of all swords"""
        self.name = None
        self.is_melee = True
        self.element = element
        self.damage = [1, 6]
        self.range = 1
        self.aoe = aoe
        self.aoe_type = aoe_type

    def attack(self, attacking, defending):
        random_damage = random.randint(self.damage[0], self.damage[1])
        attacking_power = attacking.power
        defending_armor = defending.armor
        if attacking_power < 1:
            attacking_power = 0
        if defending_armor < 1:
            defending_armor = 0
        extra_damage = (attacking_power - defending_armor) / 10
        if extra_damage < 0:
            extra_damage = 0
        else:
            extra_damage = math.ceil(extra_damage)
        total_damage = random_damage + extra_damage

        defending.health -= total_damage

        return total_damage


class sword(BaseSword):
    def __init__(self):
        super().__init__()
        self.name = "Sword"


class earth_sword(BaseSword):
    def __init__(self):
        super().__init__(element='Earth', aoe=True, aoe_type="Square;1;1")
        self.name = "Earth Sword"


class BaseBow:
    def __init__(self):
        """The base class of all bows"""


class BaseShield:
    def __init__(self):
        """The base class of all shields"""


# Magic Powers

class BaseMagic:
    def __init__(self, level):
        """The base class of all magic powers"""
        self.is_melee = False
        self.damage = None
        self.range = None
        self.aoe = True
        self.aoe_type = None
        self.level = level

    def attack(self, character, enemy):
        """This should never be called, it is overwritten inside of each individual class"""


class fire(BaseMagic):
    def __init__(self, level):
        super().__init__(level)
        self.name = "Fire"
        self.damage = [2, 4]
        self.range = 2
        self.aoe_type = "SQUARE;1"

    def attack(self, attacking, defending):
        random_damage = random.randint(self.damage[0], self.damage[1])
        attacking_power = attacking.power
        defending_armor = defending.armor
        if attacking_power < 1:
            attacking_power = 0
        if defending_armor < 1:
            defending_armor = 0
        extra_damage = (attacking_power - defending_armor) / 10
        if extra_damage < 0:
            extra_damage = 0
        else:
            extra_damage = math.ceil(extra_damage)
        total_damage = random_damage + extra_damage

        defending.health -= total_damage

        return total_damage


class air(BaseMagic):
    def __init__(self, level):
        super().__init__(level)
        self.name = "Air"
        self.damage = [1, 6]
        self.range = 3
        self.aoe = False

    def attack(self, attacking, defending):
        random_damage = random.randint(self.damage[0], self.damage[1])
        attacking_power = attacking.power
        defending_armor = defending.armor
        if attacking_power < 1:
            attacking_power = 0
        if defending_armor < 1:
            defending_armor = 0
        extra_damage = (attacking_power - defending_armor) / 10
        if extra_damage < 0:
            extra_damage = 0
        else:
            extra_damage = math.ceil(extra_damage)
        total_damage = random_damage + extra_damage

        defending.health -= total_damage

        return total_damage
