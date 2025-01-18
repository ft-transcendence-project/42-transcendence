class Utils:
    def print_colored_message(color, message):
        if color == "white":
            print(message)
        elif color == "red":
            print(f"\033[31m{message}\033[37m")
        elif color == "green":
            print(f"\033[32m{message}\033[37m")
        elif color == "yellow":
            print(f"\033[33m{message}\033[37m")
        elif color == "blue":
            print(f"\033[34m{message}\033[37m")
