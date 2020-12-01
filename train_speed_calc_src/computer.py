# -*- coding: utf-8 -*-

from ts import Ts

class Computer( object ):
    """
        #Описание класса
        Проводит расчет элемента нахождения элемента путевого развития в определенном состоянии
        Например: применяется для определения времени прохождения поезда по секции
        Идея в следущем:
            1. У нас есть шаблоны состояния интересующих нас ТС загруженные с файла конфигурации и хранимые в слворях с именем %_template
            2. Все вновь полученные ТСы мы проверяем на нужность нам и если они нас интересуют то:
                1. обновляем текущее значение ТС в словарях %_now
                2. сохраняем полученый ТС в словаре self.signals - тем самым подготавливая данные для расчета времени движения головы состава

        ##Ограничение
            Считаем, что в ТС на секцию одна запись
    """
    #public
    def check_ts_state(self):
        """
            По концу проверит, что все состояние всех ТС не равно -1, 
            Если равно - значит этот сигнал не обновился и поэтому не верна настройка этого калькулятора
        """
        #FIX ME - TODO
        pass

    def get_ts_names(self):
        ret = {**self.__self_ts_now, **self.__sibling_ts_now }
        if ( self.__constrain_now ):
            ret = {**ret, **self.__constrain_now }
        return ret

    def new_state(self, ts ):
        if ( ts.name in self.__self_ts_now ):
            self.__update_self_ts( ts )

        elif ( ts.name in self.__constrain_now ):
            self.__update_constrain( ts )

        elif ( ts.name in self.__sibling_ts_now ):
            self.__update_sibling_ts( ts )


    #private
    def __init__(self, _name, _dict ):
        #Это шаблоны загруженные из конфигурации - какое положение ТС должно быть 
        self.__self_ts_template = _dict['SELF_TS'].copy()
        self.__constrain_template = _dict['CONSTRAIN'].copy()
        self.__sibling_ts_template = _dict['SIBLING_TS'].copy()
        #Это верктора с текущими данными
        self.__self_ts_now = _dict['SELF_TS'].copy()
        self.__constrain_now = _dict['CONSTRAIN'].copy()
        self.__sibling_ts_now = _dict['SIBLING_TS'].copy()
        #Длинна участка
        self.__length = float(_dict['LENGTH'])
        #Это список с последними значениями ТС
        self.__signals = {}
        #Установим все значения переменных в неинициализированное состояние: -1

        for k in self.__self_ts_now.keys():
            self.__self_ts_now[k] = -1
        for k in self.__sibling_ts_now.keys():
            self.__sibling_ts_now[k] = -1
        if ( self.__constrain_now ):
            for k in self.__constrain_now.keys():
                self.__constrain_now[k] = -1


        print("--now--")
        print (self.__self_ts_now)
        print (self.__sibling_ts_now)
        print (self.__constrain_now)

        print("--template--")
        print (self.__self_ts_template)
        print (self.__sibling_ts_template)
        print (self.__constrain_template)



    def __update_self_ts( self, ts ):
        self.__self_ts_now[ts.name] = ts.value
        self.__signals[ts.name] = ts
        self.__compute()

    def __update_constrain( self, ts ):
        self.__constrain_now[ts.name] = ts.value
        self.__compute()


    def __update_sibling_ts( self, ts ):
        self.__sibling_ts_now[ts.name] = ts.value
        self.__signals[ts.name] = ts
        self.__compute()

    def __compute( self ):
        if ( self.__check_conditions_equals() ):
            self.__compute_inner()

    def __check_conditions_equals( self ):
        if ( self.__self_ts_template == self.__self_ts_now ):
           if ( self.__sibling_ts_template == self.__sibling_ts_now ):
               if ( self.__constrain_template == self.__constrain_now ):
                    return True
        return False

    def __find_last_sibling_ts( self ):
        """
            Вернет имя поледнего обновленного ТСа из соседних
        """
        last_ts_name = list(self.__sibling_ts_now.keys())[0]
        for key in self.__sibling_ts_now.keys():
            if ( self.__signals[last_ts_name].sec < self.__signals[key].sec ):
                last_ts_name = key
        return last_ts_name

    def __compute_inner( self ):
        """
        Это самый главный метод где происходит расчет времени движения говоывы поезда по данной секции        
        Алгорим расчета такой:
            1. Мы знаем на этом этапе, что условие расчета выполнено
            2. Находим ТС из соседей с наибольшим временем
            3. Проверяме, что время найденого ТС соседа больше времени оновления ТС секции
            4. Определяем разницу между временем соседа и своим - это будет движение поезда по этой  секции
            5. Определяем скорость движения поезда
            6. Сохраняем ее в базу данных, пока просто выводим на экран
        """
        last_ts_name = self.__find_last_sibling_ts()
        #FIX ME - считаем что в self_ts_now - только один ТС и не делаю п.3
        self_ts_name = list(self.__self_ts_now.keys())[0]

        secs_to_move = self.__signals[last_ts_name].sec - self.__signals[self_ts_name].sec
        print (f"Движение в сторону {last_ts_name}, время движения {secs_to_move} сек, время занятия секции {self_ts_name} {self.__signals[self_ts_name].sec}")
#        for ts in self.__signals.values():
#            print (ts)


def create_ts_names( comp_list ):
    ret = {}
    for cm in comp_list:
        ret = { **ret, **cm.get_ts_names() }
    return ret.keys()

def create_computers( _dict ):
    ret = []
    for c in _dict.keys():
        ret.append( Computer(c, _dict[c] ) )
    return ret