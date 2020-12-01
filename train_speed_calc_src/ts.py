# -*- coding: utf-8 -*-


class Ts( object ):
    def __init__(self, _sec, _name, _value ):
        self.name = _name
        self.sec = int(_sec )
        self.value = 0 if (-1 != _value.find('0') ) else 1


    def __str__(self):
        return (f"'name':'{self.name}', 'value':{self.value}, 'sec':{self.sec}")