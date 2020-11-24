# -*- coding: utf-8 -*-

class StateTimeCalcSimple(object):
    """
        Преобразует временной ряд состояния ТС в временные интервалы нахождения в каждом состоянии
            state - то состояние которое нас интересует
        Для случая когда для контроля состояния не нужно смотреть состояние других импульсов ТС
    """

    def __init__(self, state):
        self.close_state = state
        self.data=[]
        self.equal_sec = 0
        self.non_equal_sec = 0

    def add_value( self, sec, val, ts_name ):
        if ( self.close_state != val ):
            self.non_equal_sec = sec

            if ( 0 != self.equal_sec ):
                self.data.append( (self.non_equal_sec - self.equal_sec)/60 )
        else:
            self.equal_sec = sec

    def size(self):
        return len(self.data)

    def add_gaps( self, number ):
        for i in range( number ):
            self.data.append( None )


def from_ts_state_to_time_interval( data, ts_impl_name ):
    """
         Возвращает словарь с временами нахождения (в минутах) в 1-м состоянии и в 0-м состоянии
    """
    zero_state = StateTimeCalcSimple( state = 0 )
    one_state = StateTimeCalcSimple( state = 1 )

    for d in data:
        sec, title, value = d
        zero_state.add_value ( sec, int(value), ts_impl_name )
        one_state.add_value ( sec, int(value), ts_impl_name )


    if ( one_state.size() > zero_state.size() ):
        zero_state.add_gaps( one_state.size() - zero_state.size() )
    else:
        one_state.add_gaps( zero_state.size() - one_state.size() )

    return ( {"0":zero_state.data, "1":one_state.data} )


def write_dict_to_cvs( interval_dict, ts_impl_name, logger ):
    """
        Записывает словарь в csv file. 
        FIX ME Если по ключам массиывы разной длинны - то запишутся данные с индексами из массива нименьшей длинны
    """
    name = 'ts_'+ts_impl_name+'.csv'
    with open('ts_'+ts_impl_name+'.csv', 'w') as csvfile:
        header = list( interval_dict.keys() )
        csvfile.write("{}, {}\n".format( header[0], header[1] ) )
        val = list( interval_dict.values() )
        v1 = val[0]
        v2 = val[1]

        max_len = len(v1) if len(v1) < len(v2) else len(v2)
        for i in range( max_len ):

            try:
               csvfile.write("{}, {}\n".format( v1[i], v2[i] ) )
            except:
                pass

        csvfile.close()
        logger.info ("В файл {} сохранены состояния для сигнала ТС {} ({:d} записей)".format( name, ts_impl_name, max_len  ) )

