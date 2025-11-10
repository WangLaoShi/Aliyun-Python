class Player:
    def __init__(self,age=0,name='Player'):
        self._age = age
        self._name = name
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self,name):
        self._name = name

    @property
    def age(self):
        return self._age
    @age.setter
    def age(self,age):
        self._age = age