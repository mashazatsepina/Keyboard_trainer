def add_attempt(mode: int, speed: int, accuracy: int):
    with open("src/attempts.txt", 'r') as file:
        string = file.read()
    with open("src/attempts.txt", '+w') as file:
        file.write(str(mode) + " sec mode | " + str(speed) + " wpm | " + str(accuracy) + '%\n' + string)
    with open("src/attempts.txt", 'r') as file:
        string = file.read()
        strings = string.split("\n")
    with open("src/attempts.txt", "w") as file:
        file.write('\n'.join(strings[:10]))


        