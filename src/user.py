class User:
    def __init__(self, name):
        self.name = name
        self.password = None

    def __str__(self):
        return f'{self.name} <{self.email}>'

    def set_password(self, password):
        self.password = password
