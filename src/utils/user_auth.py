class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class AuthenticationSystem:
    def __init__(self):
        self.users = {}

    def register_user(self, username, password):
        if username in self.users:
            return False  # Username already exists
        self.users[username] = User(username, password)
        return True  # Registration successful

    def login(self, username, password):
        if username in self.users and self.users[username].password == password:
            return True  # Login successful
        return False  # Invalid credentials


# Example usage
auth_system = AuthenticationSystem()
auth_system.register_user("user1", "password1")
auth_system.register_user("user2", "password2")
print(auth_system.login("user1", "password1"))  # True
print(auth_system.login("user3", "password3"))  # False
