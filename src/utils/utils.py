import json


def generate_salt():
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def generate_hashed_password(password, salt):
    import hashlib
    return hashlib.sha256(password.encode() + salt.encode()).hexdigest()


def load_users():
    FILENAME = "users.json"

    print(f"checking if {FILENAME} exists...")

    try:
        with open(FILENAME, "r"):
            print(f"{FILENAME} found")
            pass
    except FileNotFoundError:
        print(f"{FILENAME} not found")
        with open(FILENAME, "w") as file:
            json.dump({}, file)

    with open(FILENAME, "r") as file:
        if file.read() == "":
            print(f"{FILENAME} is empty")
            return {}
        file.seek(0)  # json.load(file) is not working without this
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            print("error loading users from file")
            return {}


def save_users(users):
    print("saving users to file...")
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)
    print("users saved to file")
