# This is a stand in for the GUI program to allow testing

from character_gen import GenerateCharacter


def gen_char(chars):
    char_list = [print(GenerateCharacter()) for i in range(chars)]





while True:
    user_input = input("command: ")
    try:
        eval(user_input)
    except():
        print("Enter a valid command")

