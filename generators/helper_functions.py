import random


def roll_dice(dice, sides):
    return sum([random.randint(1, sides) for i in range(dice)])


def dress_string(string):
    """Takes a string and replaces keycoded blocks with appropriate random element
    returns a new string."""
    # this needs to be updated based on how items are generated. It is likely that
    # the funciton will be recieving a list and not a string with \n
    # TODO change this function so it returns a list
    return_string = ""
    string_list = string.split("\n")
    for line in string_list:
        chunk = line.replace("[color]", random.choice(colors))
        chunk = chunk.replace("[condition]", random.choice(condition))
        # look for die rolls
        if "{" in chunk:
            start = chunk.find("{") + 1
            end = chunk.find("}")
            roll = chunk[start:end].split("d")
            # roll the dice & replace the {roll}
            roll_result = roll_dice(int(roll[0]), int(roll[1]))
            chunk = chunk.replace(chunk[start-1:end+1], str(roll_result))
        return_string += chunk + "\n"

    return return_string