# -*- coding: utf-8 -*-


class Ts( object ):
    def __init__(self, _sec = -1, _name = '???', _value = '???' ):
        self.name = _name
        self.sec = int(_sec )
        self.value = 0 if (-1 != _value.find('пас') ) else 1 if (-1 != _value.find('акт') ) else -2
        self.is_used = False


    def __str__(self):
        return (f"'name':'{self.name}', 'value':{self.value}, 'sec':{self.sec}, 'is_used': {self.is_used}")