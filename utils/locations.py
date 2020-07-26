
from PIL import Image, ImageDraw, ImageFilter


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
        self.map_size = map_size
        self.image = None
        self._map = self._generate_map()

    def _generate_map(self):
        return_map = []
        for _ in range(self.map_size[0]):
            map_row = []
            for _ in range(self.map_size[1]):
                map_row.append(0)
            return_map.append(map_row)
        return return_map

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

    def find_closest_player(self, monster):
        ends = []
        lowest_length = float('inf')
        lowest_length_cords = None
        start = monster.last_cords
        for x in self.map:
            for y in x:
                if y in [1, 2, 3, 4]:
                    ends.append((self.map.index(x), x.index(y)))
        for end in ends:
            path = astar(self.map, start, end, monster)
            if len(path) < lowest_length:
                lowest_length = len(path)
                lowest_length_cords = path
        return lowest_length_cords

    def target_player(self, monster, player):
        path = astar(self.map, monster.last_cords, player.last_cords, monster)
        print(path)
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
        super().__init__(map_size=(9, 11))
        self.place = 'inn'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🍹'
        self.travel_locations = [garden]


class garden(Sanctum):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'garden'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌸'
        self.travel_locations = [inn, temple, market, arena, meadow]


class temple(Sanctum):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'temple'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '⛲'
        self.travel_locations = [garden]


class market(Sanctum):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'market'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🎏'
        self.travel_locations = [garden]


class arena(Sanctum):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'arena'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🔰'
        self.travel_locations = [garden]


class tavern(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'tavern'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🍺'
        self.travel_locations = [courtyard]


class courtyard(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'courtyard'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🕌'
        self.travel_locations = [meadows, tavern, dungeon, bazaar, pits]


class dungeon(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'dungeon'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '⛓'
        self.travel_locations = [courtyard]


class bazaar(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'bazaar'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🎎'
        self.travel_locations = [courtyard]


class pits(Pandaemonium):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'pits'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '💢'
        self.travel_locations = [courtyard]

        self.map[4][4] = 6


class meadow(Elysium):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'meadow'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌻'
        self.travel_locations = [garden, bridge, isle, grove]


class isle(Elysium):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'isle'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌴'
        self.travel_locations = [meadow, grove]


class grove(Elysium):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'grove'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌲'
        self.travel_locations = [meadow, isle]


class bridge(Abyss):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'bridge'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌉'
        self.travel_locations = [meadow, meadows, hall, styx, palace]


class hall(Abyss):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'hall'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌑'
        self.travel_locations = [bridge, styx, palace]


class styx(Abyss):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'styx'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '👻'
        self.travel_locations = [bridge, hall, palace]


class palace(Abyss):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'palace'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🏰'
        self.travel_locations = [bridge, hall, styx]


class meadows(Tartarus):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'meadows'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🥀'
        self.travel_locations = [bridge, courtyard, wasteland, volcano]


class wasteland(Tartarus):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'wasteland'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🦂'
        self.travel_locations = [meadows, volcano]


class volcano(Tartarus):
    def __init__(self):
        super().__init__(map_size=(9, 11))
        self.place = 'volcano'
        self.image = f'images/maps/map_{self.place}.jpg'
        self.icon = '🌋'
        self.travel_locations = [meadows, wasteland]
