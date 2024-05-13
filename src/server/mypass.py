import pwinput
import bcrypt


def extract_salt(hash_string):
    return hash_string[:31]


class Database:
    def __init__(self):
        self.database = self.InitializeDatabase()

    def InitializeDatabase(self):
        database = {}
        try:
            with open("db.txt", "r") as f:
                for line in f:
                    username, salted_hashed_password = line.strip().split(" ")
                    database[username] = salted_hashed_password
        except FileNotFoundError:
            print("Database file not found. Creating a new database file")
            with open("db.txt", "w") as f:
                pass

        return database

    def PrintDatabase(self):
        print("Printing database")
        for username, salted_hashed_password in self.database.items():
            print(f"{username}: {salted_hashed_password}")

    def SearchDatabase(self, username):
        return True if username in self.database else False

    def WriteToDatabase(self, username, salted_hashed_password):
        with open("db.txt", "a") as f:
            f.write(f"{username} {salted_hashed_password}\n")
        self.database = self.ReadFromDatabase()

    def ReadFromDatabase(self):
        database = {}
        with open("db.txt", "r") as f:
            for line in f:
                username, salted_hashed_password = line.strip().split(" ")
                database[username] = salted_hashed_password
        return database


database = Database()

while True:
    choice = input("Choose (1) to create an account or; (2) To login into an existing acccount: ")
    if choice == "1":
        # creating account
        while True:
            username = input("Please enter the user name: ")
            if database.SearchDatabase(username):
                print(f"{username} already exists. Please try another username")
            else:
                break

        while True:
            password = pwinput.pwinput("Enter your password: ")

            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode(), salt)
            # FORGOT TO DECODE WHEN WRITING TO DB!!!
            database.WriteToDatabase(username, hashed_password.decode())
            break

        print("Your account was successfully created!")

    elif choice == "2":
        print("Logging in")
        username = input("Enter your username: ")
        if database.SearchDatabase(username):
            database_salted_hashed_password = database.database[username]
            salt = extract_salt(database_salted_hashed_password)
            print(f"Salt: {salt}")

            password = pwinput.pwinput("Enter your password: ")
            userinput_salted_hashed_password = bcrypt.hashpw(password.encode(), salt.encode()).decode()

            print(f"ENTERED PASSWORD: {userinput_salted_hashed_password}")
            print(f"DATABASE PASSWORD: {database_salted_hashed_password}")

            if userinput_salted_hashed_password == database_salted_hashed_password:
                print("Login successful")
            else:
                print("Invalid password")

    elif choice == "3":
        database.PrintDatabase()
    elif choice == "9":
        exit()
    else:
        print("Invalid choice")
