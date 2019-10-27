import random
import helper_functions as helper

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
            self.equipment = self.generate_equipment(self.player_class)
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

    def generate_equipment(self, cclass):
        """
        Generate a list of equipment based on class table. Randomize and return as list
        :param cclass: string
        :return: list
        """
        equipment = []
        for line in equipment_list:
            split_by_type = line.split(":")
            if split_by_type[0] == cclass:
                weapons = split_by_type[1].split(",")
                armor = split_by_type[2].split(",")
                equipment += [random.choice(weapons), random.choice(armor)]
                equipment = [item.strip() for item in equipment]
        return equipment



chars = [print(GenerateCharacter(player_class=["unclassed","fighter","monk"])) for i in range(10)]













 # This area for testing purposes


string = "a large book with a [color] cover\n" \
         "{3d6} [color] widgets\n" \
         "A [color] quiver with {2d12} arrows\n" \
         "{1d3} broken [color] pickle statues\n" \
         "{1d6} [condition] [color] finger rapiers"












