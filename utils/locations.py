import math

import discord
from PIL import Image, ImageDraw, ImageFilter

from utils.userInfo import User

from utils.monsters import *
from utils.characters import Angel, Demon


class MapSizeError(Exception):
    """Invalid map size was given"""


class AStar:
    """A node class for A* path-finding"""
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(maze, start, end, character):
    starting_at = AStar(None, start)
    ending_at = AStar(None, end)

    open_spaces = []
    closed_spaces = []

    open_spaces.append(starting_at)

    while len(open_spaces) > 0:

        current_path_values = open_spaces[0]
        current_index = 0
        for index, item in enumerate(open_spaces):
            if item.f < current_path_values.f:
                current_path_values = item
                current_index = index

        open_spaces.pop(current_index)
        closed_spaces.append(current_path_values)

        if current_path_values == ending_at:
            path = []
            current = current_path_values
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Adjacent squares; For diagonal add in (-1, -1), (-1, 1), (1, -1), (1, 1)
            node_position = (current_path_values.position[0] + new_position[0], current_path_values.position[1] + new_position[1])
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) - 1) or node_position[1] < 0:
                continue

            if maze[node_position[0]][node_position[1]] not in [0, 1, 2, 3, 4]+character.can_pass_over:  # 0 is an open space, 1-4 are characters so we want to move to them, and character.can_pass_over is a number representing an obstacle that the character can pass over
                continue

            new_node = AStar(current_path_values, node_position)
            children.append(new_node)

        for child in children:

            for closed_child in closed_spaces:
                if child == closed_child:
                    continue

            child.g = current_path_values.g + 1
            child.h = ((child.position[0] - ending_at.position[0]) ** 2) + ((child.position[1] - ending_at.position[1]) ** 2)
            child.f = child.g + child.h

            for open_node in open_spaces:
                if child == open_node and child.g > open_node.g:
                    continue

            open_spaces.append(child)


class BaseMap:
    def __init__(self, map_size=(0, 0)):
        self.map_size = (map_size[0]+1, map_size[1]+1)
        self.image = None
        self._map = self._generate_map()
        self.monsters = []

    def _generate_map(self):
        return_map = []
        for _ in range(self.map_size[0]):
            map_row = []
            for _ in range(self.map_size[1]):
                map_row.append(0)
            return_map.append(map_row)
        return return_map

    async def start_fight(self, bot, ctx, user, channel):
        character_dump = user.active_character
        character_class_name = character_dump.split(";")[1]
        character = eval(character_class_name)(character_dump)
        character.number = 1
        location = eval(character.location.lower())()

        ctx.channel = channel

        location.place_person_on_map(character, (1, 1))
        if location.place not in ['isle', 'grove', 'hall', 'styx', 'palace', 'wasteland', 'volcano']:
            return None
        total_level = character.level

        party = [(ctx.author, character)]
        original_party = [(ctx.author, character)]
        monsters = []
        near_player = []

        for number, follower in enumerate(character.party):
            follower_discord_user = ctx.guild.get_member(follower)
            follower_user = User(bot, ctx, user=follower_discord_user)

            character_follower_dump = follower_user.active_character
            character_class_name = character_follower_dump.split(";")[1]
            follower_character = eval(character_class_name)(character_follower_dump)

            follower_character.number = number + 2
            total_level += follower_character.level

            party.append((follower_discord_user, follower_character))
            original_party.append((follower_discord_user, follower_character))
            location.place_person_on_map(follower_character, (number + 2, random.randint(1, 3)))

        spawning_monsters = math.ceil(total_level/10)

        if spawning_monsters <= 0:
            spawning_monsters = 1
        elif spawning_monsters > 5:
            spawning_monsters = 5

        for number in range(spawning_monsters):
            spawned_monster = random.choice(location.monsters)(location=location)
            monsters.append(spawned_monster)
            location.place_person_on_map(spawned_monster, (9, number+1))

        # Now we place all on the map before anyone makes a move
        image = location.draw_to_map(party[0][1], party[0][1].last_cords)
        for player in party[1:]:
            image = location.draw_to_map(player[1], player[1].last_cords, image)
        for player in monsters:
            image = location.draw_to_map(player, player.last_cords, image)

        while True:  # Main game loop
            for char in party:  # Loop over each character to give everyone a turn
                while True:  # Main player turn loop
                    discord_user = discord.utils.get(ctx.guild.members, id=ctx.author.id)
                    if char[1].health <= 0:  # Player died
                        party.remove(char)  # So we remove them from the party
                    if len(party) == 0:  # Nobody is alive
                        for dead in original_party:
                            died = User(None, None, dead[0])
                            if died.character_1 == died.active_character:
                                d_column = 'character_1'
                            elif died.character_2 == died.active_character:
                                d_column = 'character_2'
                            elif died.character_3 == died.active_character:
                                d_column = 'character_3'
                            else:
                                return
                            died.update_value(d_column, None)
                            died.update_value("active_character", None)
                        return await ctx.send("The monsters have won!")
                    elif len(monsters) == 0:
                        return await ctx.send("You have killed all the monsters!")
                    embed = discord.Embed(title="Actions", color=discord.Color.green() if not self.is_near_monster(char[1], monsters) else discord.Color.red())
                    embed.add_field(name=f"What action do you want to preform {discord_user.nick if discord_user.nick else discord_user.name}?", value=f"__Move__: **&move <up | down | left | right>**\n__Pass__: **&pass**\n{'__Attack__: **&attack**' if self.is_near_monster(char[1], monsters) else None}")
                    files = [discord.File('images/modified/modified_map.png')]
                    await ctx.send(files=files, embed=embed)
                    while True:  # Main action selection loop
                        next_move_message = await bot.wait_for('message', check=lambda check: check.author.id == char[0].id)
                        next_move = next_move_message.content.lower()
                        try:
                            if " " in next_move:
                                command, option = next_move.split(" ")
                            else:
                                command, option = next_move, None
                        except ValueError:
                            continue
                        if command in ["&m", "&move"]:
                            if option in ['u', 'up']:
                                moved, err_msg = location.move_player(char[1], (0, -1))
                                if moved:
                                    pass
                                else:
                                    await ctx.send("You cant move further up" if not err_msg else err_msg)
                                    continue
                            elif option in ['d', 'down']:
                                moved, err_msg = location.move_player(char[1], (0, 1))
                                if moved:
                                    pass
                                else:
                                    await ctx.send("You cant move further down" if not err_msg else err_msg)
                                    continue
                            elif option in ['l', 'left']:
                                moved, err_msg = location.move_player(char[1], (-1, 0))
                                if moved:
                                    pass
                                else:
                                    await ctx.send("You cant move further left" if not err_msg else err_msg)
                                    continue
                            elif option in ['r', 'right']:
                                moved, err_msg = location.move_player(char[1], (1, 0))
                                if moved:
                                    pass
                                else:
                                    await ctx.send("You cant move further right" if not err_msg else err_msg)
                                    continue
                            else:
                                continue
                        elif command in ['&a', '&att', '&attack']:
                            if option not in ['up', 'down', 'left', 'right']:
                                await ctx.send("Cord attacking not implemented yet! Check back later")
                            near_monster_list = location.is_near_monster(char[1], monsters)
                            if not near_monster_list:
                                await ctx.send("No monster was found there!")
                                continue
                            for near in near_monster_list:
                                if (char[1].last_cords[0], char[1].last_cords[1]-1) == near:
                                    near_player.append(('up', near))
                                if (char[1].last_cords[0], char[1].last_cords[1]+1) == near:
                                    near_player.append(('down', near))
                                if (char[1].last_cords[0]-1, char[1].last_cords[1]) == near:
                                    near_player.append(('left', near))
                                if (char[1].last_cords[0]+1, char[1].last_cords[1]-1) == near:
                                    near_player.append(('right', near))
                            for near, mons in near_player:
                                if near == option:
                                    player_damage, weapon = char[1].attack(mons)
                                    await ctx.send(f"{char[1].name} attacked {mons.name} with {weapon} and hit them for {player_damage} damage! {mons.name} now has {mons.health} health left!")
                                    if mons.health <= 0:
                                        monsters.remove(mons)
                        elif command in ['&pass', '&p']:
                            pass

                        # Updates the game board with the player movement
                        image = location.draw_to_map(party[0][1], party[0][1].last_cords)
                        for player in party[1:]:
                            image = location.draw_to_map(player[1], player[1].last_cords, image)
                        for monster in monsters:
                            image = location.draw_to_map(monster, monster.last_cords, image)
                        break

            for monster in monsters:
                char = self.find_closest_player(party, monster)
                moved, monster_damage = location.target_player(monster, char[1])
                if moved:
                    pass
                else:
                    if char[1].died:
                        await ctx.send(f"{monster.name} hit {char[1].name} with {monster_damage[1]} for {monster_damage[0]} damage and killed them!!")
                    else:
                        await ctx.send(f"{char[1].name} was attacked by {monster.name} using {monster_damage[1]} for {monster_damage[0]} damage! You now have {char[1].health} health left")
                image = location.draw_to_map(party[0][1], party[0][1].last_cords)
                image = location.draw_to_map(monster, monster.last_cords, image)
                for player in party[1:]:
                    image = location.draw_to_map(player[1], player[1].last_cords, image)

    def draw_to_map(self, item, location, modified_image_path=None):

        base_map = Image.open(modified_image_path if modified_image_path else self.image)
        drawing = Image.open(item.image)

        base_map.paste(drawing, (17+70*location[0], 17+70*location[1]))

        base_map.save('images/modified/modified_map.png', quality=100)

        return 'images/modified/modified_map.png'

    @staticmethod
    def is_near_monster(character, monsters):
        attackable = []
        character_cord_x, character_cord_y = character.last_cords
        possible_attack_locations = [(character_cord_x-1, character_cord_y), (character_cord_x+1, character_cord_y), (character_cord_x, character_cord_y-1), (character_cord_x, character_cord_y+1)]
        for monster in monsters:
            if monster.last_cords in possible_attack_locations:
                attackable.append(monster)
        return attackable

    def place_person_on_map(self, player, cords):
        self.map[cords[0]][cords[1]] = player.number
        player.last_cords = cords

    def move_player(self, player, cords):
        try:
            if player.last_cords[0] + cords[0] < 0 or player.last_cords[1] + cords[1] < 0 or self.map[player.last_cords[0] + cords[0]][player.last_cords[1] + cords[1]] != 0:
                return False, "That space is not accessible!"
            self.map[player.last_cords[0] + cords[0]][player.last_cords[1] + cords[1]] = player.number
            self.map[player.last_cords[0]][player.last_cords[1]] = 0
            player.last_cords = (player.last_cords[0] + cords[0], player.last_cords[1] + cords[1])
            return True, None
        except IndexError:
            return False, None

    def find_closest_player(self, characters, monster):
        if monster.target:
            for char in characters:
                if char[0].id == monster.target:
                    if char[1].health <= 0:
                        break
                    return char

        chars = [char for char in characters]
        lowest_length = float('inf')
        closest = None
        start = monster.last_cords
        for char in chars:
            path = astar(self.map, start, char[1].last_cords, monster)
            if len(path) < lowest_length:
                lowest_length = len(path)
                closest = char
                monster.target = char[0].id
        return closest

    def target_player(self, monster, player):
        path = astar(self.map, monster.last_cords, player.last_cords, monster)
        if len(path) > 2:
            self.map[path[1][0]][path[1][1]] = monster.number
            self.map[monster.last_cords[0]][monster.last_cords[1]] = 0
            monster.last_cords = path[1]
            return True, None
        else:
            return False, monster.attack(player)

    @property
    def map(self):
        return self._map

    @map.setter
    def map(self, value):
        if isinstance(tuple, value) and len(value) == 2:
            self.map_size = value
            self._map = self._generate_map()
        else:
            raise MapSizeError("Invalid Map Size Given")


# These are the base classes for each city, they specify what town/place/location is in each city. Classes will inherit from these classes
class Sanctum(BaseMap):
    def __init__(self, map_size):
        super().__init__(map_size=map_size)
        self.location = "Sanctum"
        self.places_in = [inn, garden, temple, market, arena]


class Pandaemonium(BaseMap):
    def __init__(self, map_size):
        super().__init__(map_size=map_size)
        self.location = 'Pandaemonium'
        self.places_in = [tavern, courtyard, dungeon, bazaar, pits]


class Elysium(BaseMap):
    def __init__(self, map_size):
        super().__init__(map_size=map_size)
        self.location = 'Elysium'
        self.places_in = [meadow, isle, grove]


class Abyss(BaseMap):
    def __init__(self, map_size):
        super().__init__(map_size=map_size)
        self.location = "Abyss"
        self.places_in = [bridge, hall, styx, palace]


class Tartarus(BaseMap):
    def __init__(self, map_size):
        super().__init__(map_size=map_size)
        self.location = 'Tartarus'
        self.places_in = [meadows, wasteland, volcano]


# These are each town/place/location. They tell you what location you can travel to and where they are located at, such as the inn being in the Sanctum and the isle being in Elysium
class inn(Sanctum):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'inn'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🍹'
        self.travel_locations = [garden]


class garden(Sanctum):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'garden'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌸'
        self.travel_locations = [inn, temple, market, arena, meadow]


class temple(Sanctum):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'temple'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '⛲'
        self.travel_locations = [garden]


class market(Sanctum):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'market'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🎏'
        self.travel_locations = [garden]


class arena(Sanctum):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'arena'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🔰'
        self.travel_locations = [garden]


class tavern(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'tavern'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🍺'
        self.travel_locations = [courtyard]


class courtyard(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'courtyard'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🕌'
        self.travel_locations = [meadows, tavern, dungeon, bazaar, pits]


class dungeon(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'dungeon'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '⛓'
        self.travel_locations = [courtyard]


class bazaar(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'bazaar'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🎎'
        self.travel_locations = [courtyard]


class pits(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'pits'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '💢'
        self.travel_locations = [courtyard]

        self.map[4][4] = 6


class meadow(Elysium):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'meadow'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌻'
        self.travel_locations = [garden, bridge, isle, grove]


class isle(Elysium):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'isle'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌴'
        self.travel_locations = [meadow, grove]


class grove(Elysium):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'grove'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌲'
        self.travel_locations = [meadow, isle]


class bridge(Abyss):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'bridge'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌉'
        self.travel_locations = [meadow, meadows, hall, styx, palace]


class hall(Abyss):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'hall'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌑'
        self.travel_locations = [bridge, styx, palace]


class styx(Abyss):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'styx'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '👻'
        self.travel_locations = [bridge, hall, palace]
        self.monsters = [Ghost]


class palace(Abyss):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'palace'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🏰'
        self.travel_locations = [bridge, hall, styx]


class meadows(Tartarus):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'meadows'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🥀'
        self.travel_locations = [bridge, courtyard, wasteland, volcano]


class wasteland(Tartarus):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'wasteland'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🦂'
        self.travel_locations = [meadows, volcano]


class volcano(Tartarus):
    def __init__(self):
        super().__init__(map_size=(11, 9))
        self.place = 'volcano'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌋'
        self.travel_locations = [meadows, wasteland]
