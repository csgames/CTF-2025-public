import os

def create_output(filename_from: str, filename_to: str):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    letter = "piyrwouteqljgdakhfsmbcznvx"

    with open(filename_from,'r') as f:
        msg = f.read()

    msg = msg.replace("FLAG", os.environ["FLAG"])

    output = ""

    for char in msg:
        if char in alphabet:
            output += letter[alphabet.index(char)]
        else:
            output += char

    with open(filename_to, "w") as f:
        f.write(output)

create_output("francais.txt", "fr.txt")
create_output("english.txt", "en.txt")
