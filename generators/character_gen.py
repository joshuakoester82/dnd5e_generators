import random
import sqlite3

# region Load variables from file
with open("../lists/colors.txt") as f:
    colors = f.read().split("\n")

with open("../lists/materials.txt") as f:
    materials = f.read().split("\n")

with open("../lists/condition.txt") as f:
    condition = f.read().split("\n")

with open("../lists/race_modifiers.txt") as f:
    race_modifiers = f.read().split("\n")

with open("../lists/age_ranges.txt") as f:
    age_ranges = f.read().split("\n")

with open("../lists/class_ability_order.txt") as f:
    class_ability_order = f.read().split("\n")

with open("../lists/class_equipment.txt") as f:
    class_equipment = f.read().split("\n")

# endregion
# region Load database and prepare cursor
conn = sqlite3.Connection("../db/generators.db")
c = conn.cursor()
# endregion



class GenerateCharacter:
    """
    Generates a random character from passed in parameters. If none are supplied generates a character
    randomly
    """
    def __init__(self, sex=None, age=None, race=None, player_class=None, lvl=None, name=None, ability_scores=None,
                 equipment=None):
        if sex is None:
            self.sex = random.choice(["male", "female"])
        else:
            self.sex = sex
        if race is None:
            self.race = "human" # default race is human
        else:
            self.race = random.choice(race)
        if age is None:
            self.age = self.generate_age(age_ranges, self.race)
        if player_class is None:
            self.player_class = "unclassed"
        else:
            self.player_class = random.choice(player_class)
        if lvl is None:
            self.lvl = 1
        else:
            self.lvl = lvl
        if name is None:
            self.name = self.generate_name()
        else:
            self.name = name
        if ability_scores is None:
            self.ability_scores = self.roll_ability_scores()
            self.map_ability_scores()
            self.apply_racial_bonuses()
        else:
            self.ability_scores = ability_scores
        if equipment is None:
            self.equipment = self.get_gear(self.get_loadout(self.player_class))
        else:
            self.equipment = equipment

    def __repr__(self):
        return f"{self.name}, a {self.age} year old {self.sex} {self.race} {self.player_class} of lvl {self.lvl} " \
               f"with {self.apply_attribute_bonuses(self.ability_scores)}\n" \
               f"wearing {self.equipment}\n"


    def generate_name(self):
        """
        Generate a name from first_name, last_name lists.
        :return: string
        """
        with open(f"../lists/{self.race}_{self.sex}_first.txt") as f:
            first_names_list = f.read().split("\n")
        with open(f"../lists/{self.race}_surname.txt") as f:
            last_names_list = f.read().split("\n")
        first_name = random.choice(first_names_list).strip().capitalize()
        last_name = random.choice(last_names_list).strip().capitalize()
        return f"{first_name} {last_name}"

    def roll_ability_scores(self, randomized=False):
        """
        Randomly rolls ability scores using the 4d6 remove the lowest method.
        :param randomized: Bool
        :return: list
        """
        score_list = []
        for i in range(6):
            working_list = [random.randint(1,6) for i in range(4)]
            score_list.append(sum(working_list) - min(working_list))
        return score_list

    def generate_age(self, ages, race):
        """
        Generate an age from the age chart found in age_ranges.txt
        :param ages: list
        :param race: string
        :return: int
        """
        for item in ages:
            parsed = item.split(":")
            if parsed[0] == self.race:
                ages = parsed[1].split("-")
                return random.randint(int(ages[0]), int(ages[1]))

    def map_ability_scores(self, class_ability_order=class_ability_order):
        """
        map ability scores from ability_scores to dictionary with abilities
        weighted by class
        :param class_ability_order: list
        :return: None
        """
        self.ability_scores.sort()
        for cls in class_ability_order:
            parsed = cls.split(":")
            if parsed[0].strip() == self.player_class:
                ability_dict = {"str":0,"dex":0,"con":0,"int":0,"wis":0,"cha":0}
                if parsed[1] != "":  # Has a class, distribute accordingly
                    order_list = parsed[1].split(",")
                    order_list = [item.strip() for item in order_list]
                    for ability in order_list:
                        ability_dict[ability] = self.ability_scores.pop()
                    self.ability_scores = ability_dict
                else:  # unclassed - distribute randomly
                    random.shuffle(self.ability_scores)
                    for key in ability_dict:
                        ability_dict[key] = self.ability_scores.pop()
                    self.ability_scores = ability_dict

    def apply_racial_bonuses(self, race_modifiers=race_modifiers):
        """
        Applies the racial modifiers to player ability scores
        :param race_modifiers: list
        :return: None
        """
        for item in race_modifiers:
            parsed = item.split("|")
            if parsed[0] == self.race:
                parsed_modifiers = parsed[1].split(",")
                for item in parsed_modifiers:
                    attribute = item.split(":")
                    attribute[0] = attribute[0].strip()
                    attribute[1] = attribute[1].strip()
                    self.ability_scores[attribute[0]] += eval(attribute[1])

    def apply_attribute_bonuses(self, attributes):
        """
        Take the ability_scores dict, convert each key value pair into a string representation
        with roll bonuses applied and return as string
        :param attributes: dict
        :return: string
        """
        string_list = []
        for key, value in attributes.items():
            chunk = f"{key.upper()}:{value}"
            bonus = (int(value) // 2) - 5
            if bonus != 0:
                chunk += f"({bonus:+})"
            string_list.append(chunk)
        return ", ".join(string_list)

    def get_loadout(self, cclass):
        """
        Select a loadout from the loadout table
        :param cclass: str
        :return: tuple
        """
        table = c.execute(f"""SELECT * FROM loadouts WHERE cclass = '{cclass}'""").fetchall()
        return random.choice(table)

    def get_gear(self, loadout):
        """
        Constructs a dictionary containing character equipment data (melee weapon, ranged weapon, armor, shield, items)
        Dictionary is constructed with sqlite queries. gen_query() is used to generate some queries
        :param loadout: tuple
        :return: dict
        """
        gear_dict, list_wpn_melee, list_wpn_ranged, list_items = {}, [], [], []

        # melee weapon
        melee_query = self.gen_query(loadout, 1, "weapons", "type")
        for i in range(len(melee_query)):
            list_wpn_melee.append(random.choice(c.execute(melee_query[i]).fetchall()))

        # ranged weapon
        ranged_query = self.gen_query(loadout, 2, "weapons", "type")
        for i in range(len(ranged_query)):
            list_wpn_ranged.append(random.choice(c.execute(ranged_query[i]).fetchall()))

        # armor
        armor_query = self.gen_query(loadout, 3, "armor", "type")
        armor = random.choice(c.execute(armor_query[0]).fetchall())

        # shield (simply Shield or None)
        shield = loadout[4]

        # Items
        item_row = loadout[5].split(",")
        for item in item_row:
            item_count, item_type = item.split()[0].split("-"), item.split()[1:]
            if len(item_count) > 1:
                item_count = random.choice(range(int(item_count[0]), int(item_count[1]) + 1))
            else:
                item_count = int(item_count[0])

            for i in range(item_count):
                list_items.append(random.choice(c.execute(
                    f"""SELECT * FROM adventuring_gear WHERE type LIKE '%{item_type[0]}%'""").fetchall()))

        # update gear dictionary
        gear_dict["melee"] = list_wpn_melee
        gear_dict["ranged"] = list_wpn_ranged
        gear_dict["armor"] = armor
        gear_dict["shield"] = shield
        gear_dict["items"] = list_items

        return gear_dict

    def gen_query(self, loadout, index, table, column):
        """
        Helper function.
        Constructs a list of complex SQL queries to be used in get_gear(). By complex I mean containing more than one
        LIKE statement.

        :param loadout: tuple
        :param index: int
        :param table: str
        :param column: str
        :return: list
        """
        return_list = []
        query_list = loadout[index].split(",")  # split cell into separate item queries

        for weapon in query_list:
            query_elements = weapon.split()  # split query into each query element
            for i, element in enumerate(query_elements):
                if i == 0:
                    query = f"SELECT * FROM {table} WHERE {column} LIKE '%{element}%'"
                else:
                    query += f" AND type LIKE '%{element}%'"
            return_list.append(query)

        return return_list



chars = [print(GenerateCharacter(player_class=["fighter"])) for i in range(10)]















 # This area for testing purposes


string = "a large book with a [color] cover\n" \
         "{3d6} [color] widgets\n" \
         "A [color] quiver with {2d12} arrows\n" \
         "{1d3} broken [color] pickle statues\n" \
         "{1d6} [condition] [color] finger rapiers"












