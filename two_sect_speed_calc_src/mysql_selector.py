# -*- coding: utf-8 -*-

import config as cfg
import mysql.connector
import logging,sys
from ts import Ts

#{'computer_name': 'НАП', 'move_sec': 45, 'length': 125.0, 'speed_kmh': 10.0, 'move_to_ts_name': 'Н1ИП', 'self_ts_name': 'НАП(к)', 'self_busy_sec': 1605530175}
create_speed_train_table="CREATE TABLE IF NOT EXISTS two_sect_speed (who VARCHAR(100), sect1_name VARCHAR(100), sect1_speed_kmh FLOAT, sect1_busy_sec INT, sect2_name VARCHAR(100), sect2_speed_kmh FLOAT, sect2_busy_sec INT, PRIMARY KEY(who, sect1_busy_sec, sect2_busy_sec) ) ENGINE=MYISAM "

class MysqlSelector(object):
    def __init__( self, logger, config_file ):
        self.logger = logger
        self.insert_sql_list = []
        ip, db, user = cfg.get_mysql_server_config( config_file )
        self.logger.info("MySQL config: 'ip':'{}', 'db':'{}', 'user':'{}'".format(ip, db, user) )
        self.cnx = mysql.connector.connect( user=user, database=db, host=ip )
        self.logger.info("MySQL connected".format() )
        cursor = self.cnx.cursor()
        cursor.execute( "SET NAMES 'latin1'" )
        cursor.execute( create_speed_train_table )



    def handle_signals( self, list_of_ts_names, computers ):
        """
            Получает список ТСов и метод который может передать эти сигналы в калькуляторы
        """
        in_statement = "'"
        in_statement += ",".join( e for e in list_of_ts_names ).replace(",","','")
        in_statement += "'"
        sql_str = f"SELECT DISTINCT sec,who,value FROM loglist WHERE kind='Импульс.ТЗК' AND who IN ({in_statement}) ORDER BY sec ASC"
        cursor = self.cnx.cursor()
        cursor.execute( sql_str )
        #очистим список команд вуставки данных
        self.insert_sql_list.clear()

        #обработкаем ТС
        for (sec, who, value) in cursor:
            for cm in computers:
                cm.new_state( Ts(sec, who, value) )

        #удалим старые записи
        self.delete_from_train_speed()
        #когда проверили - смотрим что насчитали и соханяем в БД
        for sql in self.insert_sql_list:
            try:
                cursor.execute( sql )
            except:
                self.logger.error ( f"BAD query: {sql} err: {sys.exc_info()[1]}\n" )

        cursor.close()
        self.logger.info( f"Загружено в БД {len(self.insert_sql_list)} записей с рассчитанными скоростями")
        self.insert_sql_list.clear()

    def delete_from_train_speed( self ):
        cursor = self.cnx.cursor()
        cursor.execute('delete from two_sect_speed')
        cursor.close()

    def insert_into_train_speed( self, decr_dict ):
        dd = decr_dict
        sql = f"REPLACE INTO two_sect_speed (who, sect1_name, sect1_speed_kmh, sect1_busy_sec, sect2_name, sect2_speed_kmh, sect2_busy_sec ) VALUES ('{dd['who']}', '{dd['sect1_name']}', {dd['sect1_speed_kmh']}, {dd['sect1_busy_sec']}, '{dd['sect2_name']}', {dd['sect2_speed_kmh']}, {dd['sect2_busy_sec']})"
        self.insert_sql_list.append(sql)

    #stage_2 --- не сделано
    def save_train_speed_to_csv( self, path ):
        with open(path, 'w') as f:
            cursor = self.cnx.cursor()
            cursor.execute('select who, sect1_name, sect1_speed_kmh, sect1_busy_sec, sect2_name, sect2_speed_kmh, sect2_busy_sec from two_sect_speed')
            f.write('who, sect1_name, sect1_speed_kmh, sect1_busy_sec, sect2_name, sect2_speed_kmh, sect2_busy_sec\n')
            for (who, sect1_name, sect1_speed_kmh, sect1_busy_sec, sect2_name, sect2_speed_kmh, sect2_busy_sec) in cursor:
                f.write(f'{who}, {sect1_name}, {sect1_speed_kmh}, {sect1_busy_sec}, {sect2_name}, {sect2_speed_kmh}, {sect2_busy_sec}\n')
            cursor.close()
            f.close()
#----------------------OLD----------------------------

    def get_data_from_ts( self, ts_name, limit ):
        sql_req= u"select from_unixtime(sec) as time, sec, who, value from loglist where kind='Импульс.ТЗК' and who IN ('{}') limit {:d}".format(ts_name, limit)
        return self.select2ict( sql_req )


    def select2ict( self, sql_str ):
        cursor = self.cnx.cursor()
        cursor.execute( sql_str )

        lst = []
        for (time, sec, who, value) in cursor:
            lst.append( [ sec, who, '0' if value.find("пассивен") != -1 else '1' ] )
        cursor.close()
        return lst


    def store_decriptive_staticsics(self, descrip, ts_name ):
        cursor = self.cnx.cursor()
        for i in descrip:
            qu = f"REPLACE INTO descriptive_statistics (ts_name, state, mean, std, first_quantile, median, third_quantile, min, max) VALUES ('{ts_name}', {i}, {descrip[i]['mean']}, {descrip[i]['std']}, {descrip[i]['25%']}, {descrip[i]['50%']}, {descrip[i]['75%']}, {descrip[i]['min']}, {descrip[i]['max']} )"
            try:
                cursor.execute( qu )
            except:
                self.logger.error ( f"BAD query: {qu}" )
                print (descrip[i])


    def select_decriptive_statictics( self, mask ):
        cursor = self.cnx.cursor()
        sql_str = "SELECT ts_name, state, mean, std, first_quantile, median, third_quantile, min, max FROM descriptive_statistics WHERE ts_name LIKE '%{}' ORDER BY ts_name, state".format(mask)
        print (sql_str)
        cursor.execute( sql_str )

        ret = {}
        for (ts_name, state, mean, std, first_quantile, median, third_quantile, minz, maxz) in cursor:
            if ( ts_name not in ret.keys() ):
                ret[ts_name] = {}
            ret[ts_name][state] = {}
            ret[ts_name][state]['mean'] = mean
            ret[ts_name][state]['std'] = std
            ret[ts_name][state]['min'] = minz
            ret[ts_name][state]['25%'] = first_quantile
            ret[ts_name][state]['50%'] = median
            ret[ts_name][state]['75%'] = third_quantile
            ret[ts_name][state]['max'] = maxz
        cursor.close()
        return ret

