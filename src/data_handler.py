# -*- coding: utf-8 -*-

class FromState2State(object):
    def __init__(self, close_state_):
        self.close_state = close_state_
        self.data=[]
        self.equal_sec = 0
        self.non_equal_sec = 0

    def add_value( self, sec, val ):
        if ( self.close_state == val ):
            self.equal_sec = sec
            if ( 0 != self.non_equal_sec ):
                self.data.append(self.equal_sec - self.non_equal_sec )
        else:
            self.non_equal_sec = sec

    def size(self):
        return len(self.data)

    def add_none( self, number ):
        for i in range( number ):
            self.data.append( None )

def from_ts_state_to_time_interval( data ):
    d1to0 = FromState2State( 0 )
    d0to1 = FromState2State( 1 )

    for d in data:
        sec, title, value = d
        d1to0.add_value ( sec, int(value) )
        d0to1.add_value ( sec, int(value) )

    if ( d1to0.size() > d0to1.size() ):
        d0to1.add_none( d1to0.size() - d0to1.size() )
    else:
        d1to0.add_none( d0to1.size() - d1to0.size() )

    return ( {"to_one_state_interval_in_sec":d0to1.data, "to_zero_state_interval_in_sec":d1to0.data} )


def write_dict_to_cvs( dct, ts, logger ):
    name = 'ts_'+ts+'.csv'
    with open('ts_'+ts+'.csv', 'w') as csvfile:
        header = list(dct.keys())
        csvfile.write("{}, {}\n".format( header[0], header[1] ) )
        val = list(dct.values())
        v1 = val[0]
        v2 = val[1]

        for i in range(len(v1)):
            csvfile.write("{}, {}\n".format( v1[i], v2[i] ) )

        csvfile.close()
        logger.info ("В файл {} сохранены состояния для сигнала ТС {} ({:d} записей)".format( name, ts, len(v1) ) )
