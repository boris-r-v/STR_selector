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
    def name(self):
        return self.__name

    def check_ts_states(self, logger):
        """
            По концу проверит, что все состояние всех ТС не равно -1, 
            Если равно - значит этот сигнал не обновился и поэтому не верна настройка этого калькулятора
        """
        for k in self.__self_ts_now.keys():
            if ( -1 == self.__self_ts_now[k] ):
                logger.error(f"Калькулятор скорости '{self.__name}', не нашел ТС '{k}' - ошибка в имени ТС")
        for k in self.__sibling_ts_now.keys():
            if ( -1 == self.__sibling_ts_now[k] ):
                logger.error(f"Калькулятор скорости '{self.__name}', не нашел ТС '{k}' - ошибка в имени ТС")
        if ( self.__constrain_now ):
            for k in self.__constrain_now.keys():
                if ( -1 == self.__constrain_now[k] ):
                    logger.error(f"Калькулятор скорости '{self.__name}', не нашел ТС '{k}' - ошибка в имени ТС")

    def get_ts_names(self):
        ret = {**self.__self_ts_now, **self.__sibling_ts_now }
        if ( self.__constrain_now ):
            ret = {**ret, **self.__constrain_now }
        return ret

    def new_state(self, ts ):
        if ( ts.name in self.__self_ts_now ):
            self.__update_self_ts( ts )

        elif ( ts.name in self.__sibling_ts_now ):
            self.__update_sibling_ts( ts )

        elif ( self.__constrain_now and ts.name in self.__constrain_now ):
            self.__update_constrain( ts )

    #private
    def __init__(self, _name, _dict, _logger, _db, _anomaly_speed, _path_to_file ):
        self.__db = _db
        self.__name = _name
        self.__logger = _logger
        self.__anomaly_speed = _anomaly_speed
        self.__path_to_file = _path_to_file
        #Это шаблоны загруженные из конфигурации - какое положение ТС должно быть 
        self.__self_ts_template = _dict['SELF_TS']
        self.__constrain_template = _dict['CONSTRAIN']
        self.__sibling_ts_template = _dict['SIBLING_TS']
        #Это верктора с текущими данными
        self.__self_ts_now = _dict['SELF_TS'].copy()
        self.__constrain_now = self.__constrain_template.copy() if self.__constrain_template else None
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


    def __update_self_ts( self, ts ):
        self.__self_ts_now[ts.name] = ts.value
        self.__signals[ts.name] = ts

    def __update_constrain( self, ts ):
        self.__constrain_now[ts.name] = ts.value

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
            0. Мы знаем на этом этапе, что условие расчета выполнено
            1. Проверяем, что у нас изменялось состояние своего ТС после прошлого расчета
            2. Находим ТС из соседей с наибольшим временем
            3. Проверяме, что время найденого ТС соседа больше времени оновления ТС секции
            4. Определяем разницу между временем соседа и своим - это будет движение поезда по этой  секции
            5. Помечаем ТС состояния своей секции как уже использованный
            6. Сохраняем данные в базу данных, определяем скорость движения поезда
        """
        #p.0
        #FIX ME - считаем что в self_ts_now - только один ТС и не делаю п.3
        self_ts_name = list(self.__self_ts_now.keys())[0]
        #p.1
        if ( self.__signals[self_ts_name].is_used ):
#FIX ME - таких записей выводиться до черта            self.__logger.warning (f"{self.__name} - Повторное занятие соседа при неизменном состоянии участка в {self.__signals[self_ts_name].sec}")
            return
        #p.2
        last_ts_name = self.__find_last_sibling_ts()
        #p.4
        secs_to_move = self.__signals[last_ts_name].sec - self.__signals[self_ts_name].sec
        #p.6
        dct = { 'computer_name': self.__name,
                'move_sec' : secs_to_move,
                'length' : self.__length,
                'speed_kmh': 3.6*self.__length/secs_to_move,
                'move_to_ts_name': last_ts_name,
                'self_ts_name':self_ts_name,
                'self_busy_sec': self.__signals[self_ts_name].sec,
                }

        if ( secs_to_move > 0 ):
            self.__db.insert_into_train_speed( dct )
        else:
            self.__logger.error ("Скорость отрицательна {dct}") 

        if ( dct['speed_kmh'] > self.__anomaly_speed ):
            #show detail:
            print (f"Аномально большая скорость {dct['speed_kmh']}")
            print (f"Движение по {self_ts_name} в сторону {last_ts_name}, время движения {secs_to_move}сек, скорость: {round(dct['speed_kmh'],2)}км/ч, время занятия: {self.__signals[self_ts_name].sec}")
            for ts in self.__signals.values():
                print (ts)
            print ("---------")

        #p.5 
        self.__signals[self_ts_name].is_used = True

def check_states( comp_list, logger ):
    """
        После выполнения сборки данных, проходит по всем калькуляторам и смотрит, что в  них не осталось импульсов ТС  со значением -1
            т.е. все импульсы были обновлены в ходе работы - значит адаптация верная
    """
    for cm in comp_list:
        cm.check_ts_states( logger )

def create_ts_names( comp_list ):
    ret = {}
    for cm in comp_list:
        ret = { **ret, **cm.get_ts_names() }
    return ret.keys()

def create_computers( _dict, _logger, _db, anomaly_speed, path_to_file ):
    ret = []
    for c in _dict.keys():
        ret.append( Computer(c, _dict[c], _logger, _db, anomaly_speed, path_to_file ) )
    return ret




#------------------Graveyard of bad ideas------------
"""
            print (f"\tДвижение по {self_ts_name} в сторону {last_ts_name}, время движения {secs_to_move}сек, скорость: {round(dct['speed_kmh'],2)}км/ч, время занятия: {self.__signals[self_ts_name].sec}")
            for ts in self.__signals.values():
                print ("\t"+str(ts))



            with open(self.__path_to_file,'a' ) as f:
                f.write(f"Движение по {self_ts_name} в сторону {last_ts_name}, время движения {secs_to_move}сек, скорость: {round(dct['speed_kmh'],2)}км/ч, время занятия: {self.__signals[self_ts_name].sec}\n")
                for ts in self.__signals.values():
                    f.write(str(ts)+'\n')
                f.write ("---------\n")
                f.close()
"""




