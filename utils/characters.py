import random
from utils.weapons import *


class BaseCharacter:
    def __init__(self, initial_data):
        info = initial_data.split(";")
        self.number = None
        self.last_cords = None

        self._name = info[0]
        self._type = info[1]
        self._location = info[2]

        self._level = eval(info[3])
        self._last_level = eval(info[4])

        self._level_up_xp = eval(info[5])
        self._display_xp = eval(info[6])
        self._xp = eval(info[7])

        self._health = eval(info[8])
        self._armor = eval(info[9])

        self._weapon_slot_one = info[10]
        self._weapon_slot_two = info[11]

        self._magic = eval(info[12])
        self._manna = eval(info[13])

        self._abilities = eval(info[14])
        self._perks = eval(info[15])
        self._known_locations = eval(info[16])

        self._points = eval(info[17])
        self._power = eval(info[18])
        self._speed = eval(info[19])
        self._knowledge = eval(info[20])

        self._party_master = eval(info[21])
        self._party = eval(info[22])
        self._in_party = eval(info[23])

        self._profile_image = info[24]
        self._image = 'images/characters/demon.png'

        self._roles = eval(info[25])

        self.char_dump = initial_data

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def location(self):
        return self._location

    @property
    def level(self):
        return self._level

    @property
    def last_level(self):
        return self._last_level

    @property
    def level_up_xp(self):
        return self._level_up_xp

    @property
    def display_xp(self):
        return self._display_xp

    @property
    def xp(self):
        return self._xp

    @property
    def health(self):
        return self._health

    @property
    def armor(self):
        return self._armor

    @property
    def weapon_slot_one(self):
        return self._weapon_slot_one

    @property
    def weapon_slot_two(self):
        return self._weapon_slot_two

    @property
    def magic(self):
        return self._magic

    @property
    def manna(self):
        return self._manna

    @property
    def abilities(self):
        return self._abilities

    @property
    def perks(self):
        return self._perks

    @property
    def known_locations(self):
        return self._known_locations

    @property
    def points(self):
        return self._points

    @property
    def power(self):
        return self._power

    @property
    def speed(self):
        return self._speed

    @property
    def knowledge(self):
        return self._knowledge

    @property
    def party_master(self):
        return self._party_master

    @property
    def party(self):
        return self._party

    @property
    def in_party(self):
        return self._in_party

    @property
    def profile_image(self):
        return self._profile_image

    @property
    def image(self):
        return self._image

    @property
    def roles(self):
        return self._roles

    @name.setter
    def name(self, value):
        self._name = value
        self.update_dump()

    @type.setter
    def type(self, value):
        self._type = value
        self.update_dump()

    @location.setter
    def location(self, value):
        self._location = value
        self.update_dump()

    @level.setter
    def level(self, value):
        self._level = value
        self.update_dump()

    @last_level.setter
    def last_level(self, value):
        self._last_level = value
        self.update_dump()

    @level_up_xp.setter
    def level_up_xp(self, value):
        self._level_up_xp = value
        self.update_dump()

    @display_xp.setter
    def display_xp(self, value):
        self._display_xp = value
        self.update_dump()

    @xp.setter
    def xp(self, value):
        self._xp = value
        self.update_dump()

    @health.setter
    def health(self, value):
        self._health = value
        self.update_dump()

    @armor.setter
    def armor(self, value):
        self._armor = value
        self.update_dump()

    @weapon_slot_one.setter
    def weapon_slot_one(self, value):
        self._weapon_slot_one = value
        self.update_dump()

    @weapon_slot_two.setter
    def weapon_slot_two(self, value):
        self._weapon_slot_two = value
        self.update_dump()

    @magic.setter
    def magic(self, value):
        self._magic = value
        self.update_dump()

    @manna.setter
    def manna(self, value):
        self._manna = value
        self.update_dump()

    @abilities.setter
    def abilities(self, value):
        self._abilities = value
        self.update_dump()

    @perks.setter
    def perks(self, value):
        self._perks = value
        self.update_dump()

    @known_locations.setter
    def known_locations(self, value):
        self._known_locations = value
        self.update_dump()

    @points.setter
    def points(self, value):
        self._points = value
        self.update_dump()

    @power.setter
    def power(self, value):
        self._power = value
        self.update_dump()

    @speed.setter
    def speed(self, value):
        self._speed = value
        self.update_dump()

    @knowledge.setter
    def knowledge(self, value):
        self._knowledge = value
        self.update_dump()

    @party_master.setter
    def party_master(self, value):
        self._party_master = value
        self.update_dump()

    @party.setter
    def party(self, value):
        self._party = value
        self.update_dump()

    @in_party.setter
    def in_party(self, value):
        self._in_party = value
        self.update_dump()

    @profile_image.setter
    def profile_image(self, value):
        self._profile_image = value
        self.update_dump()

    @image.setter
    def image(self, value):
        self._image = value
        self.update_dump()

    @roles.setter
    def roles(self, value):
        self._roles = value
        self.update_dump()

    def update_dump(self):
        self.char_dump = f"{self.name};{self.type};{self.location};{self.level};{self.last_level};{self.level_up_xp};{self.display_xp};{self.xp};{self.health};{self.armor};{self.weapon_slot_one};{self.weapon_slot_two};{self.magic};{self.manna};{self.abilities};{self.perks};{self.known_locations};{self.points};{self.power};{self.speed};{self.knowledge};{self.party_master};{self.party};{self.in_party};{self.profile_image};{self.roles}"

    def attack(self, monster):
        attack_times = 1
        attacked = None

        weapon_1 = eval(f"{self.weapon_slot_one}()")
        weapon_2 = eval(f"{self.weapon_slot_two}()")

        if weapon_1.name == weapon_2.name:
            attack_times = 2

        for _ in range(attack_times):
            attacked = weapon_1.attack(self, monster)
        return attacked, weapon_1.name


class Demon(BaseCharacter):
    def __init__(self, initial_data):
        super().__init__(initial_data)
        self.type = "Demon"


class Angel(BaseCharacter):
    def __init__(self, initial_data):
        super().__init__(initial_data)
        self.type = "Angel"
