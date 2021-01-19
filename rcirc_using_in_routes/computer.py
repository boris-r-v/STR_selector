# -*- coding: utf-8 -*-

from ts import Ts

class Computer( object ):
    """
        #Описание класса
        Проводит расчет элемента нахождения элемента путевого развития в замкнутом состоянии
        ##Ограничение
            Считаем, что в ТС на секцию одна запись
    """
    #public
    def name(self):
        return self.__name

    def new_state( self, ts, insert_sql_list ):
        if ( ts.name == self.__ts_name ):
            self.__state_sec[ts.value] = ts.sec
            if( ts.value == self.__free_state ):
                self.__calc_time_inner( insert_sql_list )

    def get_ts_names(self):
        return {self.__ts_name:0}

    def get_states(self):
        return self.__busy_time

    #private
    def __init__(self, _name, _dict, _logger, _db ):
        self.__name = _name
        self.__db = _db
        self.__logger = _logger
        self.__ts_name = list(_dict['SELF_TS'].keys() )[0]
        self.__free_state = _dict['SELF_TS'][self.__ts_name]

        _logger.info ( f"{_name} computer was born: ts: '{self.__ts_name}', free state: '{self.__free_state}'" )
        self.__state_sec = {}   #словарь с парами имя сигнала : время обновления

    def __calc_time_inner(self, insert_sql_list ):
        if ( 2 != (len(self.__state_sec) ) ):
            return
        free_sec = self.__state_sec[self.__free_state]
        busy_sec = self.__state_sec[1] if (0 == self.__free_state) else self.__state_sec[0]
        busy_time_sec = free_sec - busy_sec

        if ( busy_time_sec > 0 ):
            dct = { 'computer_name': self.__name,
                    'busy_time_sec': busy_time_sec,
                    'busy_time_min': busy_time_sec / 60,
                    'self_free_sec': free_sec
                  }
            insert_sql_list.append(dct)
        else:
            self.__logger.warning (f"{self.__name} продолжительность замыкания меньше нуля замкнули {busy_sec} разомкнули в {free_sec}, пропускаем эти события")


def create_ts_names( comp_list ):
    ret = {}
    for cm in comp_list:
        ret = { **ret, **cm.get_ts_names() }
    return ret.keys()

def create_computers( _dict, _logger, _db ):
    ret = []
    for c in _dict.keys():
        ret.append( Computer(c, _dict[c], _logger, _db ) )
    return ret




#------------------Graveyard of bad ideas------------
"""


"""




