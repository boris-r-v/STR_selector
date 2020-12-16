# -*- coding: utf-8 -*-

import config as cfg
import datetime as dt
import mysql.connector
from ts import Ts

rcirc_in_route_ct = "CREATE TABLE IF NOT EXISTS rcirc_in_route ( name VARCHAR(100), sec INT, min FLOAT, free_sec INT) ENGINE=MYISAM "

class MysqlSelector(object):
    def __init__( self, logger, config_file ):
        self.logger = logger
        self.insert_sql_list = []

        ip, db, user = cfg.get_mysql_server_config( config_file )
        logger.info("MySQL config: 'ip':'{}', 'db':'{}', 'user':'{}'".format(ip, db, user) )
        self.cnx = mysql.connector.connect( user=user, database=db, host=ip )
        logger.info("MySQL connected".format() )
        cursor = self.cnx.cursor()
        cursor.execute( "SET NAMES 'latin1'" )
        cursor.execute( rcirc_in_route_ct )

    def handle_ts_signals( self, list_of_ts_names, computers ):
        """
            Получает список ТСов и список калькуляторов метод который может передать эти сигналы в калькуляторы
        """
        in_statement = "'"
        in_statement += ",".join( e for e in list_of_ts_names ).replace(",","','")
        in_statement += "'"
        sql_req= u"SELECT sec, who, value FROM loglist WHERE kind='Импульс.ТЗК' and who IN ({})".format(in_statement)

        cursor = self.cnx.cursor()
        cursor.execute( sql_req )

        #очистим список команд вуставки данных
        self.insert_sql_list.clear()

        for (sec, who, value) in cursor:
            for cm in computers:
                cm.new_state( Ts(sec, who, value), self.insert_sql_list )
        cursor.close()

        #Рассчитанные данные сохраним в БД
        cursor = self.cnx.cursor()
        cursor.execute( "DELETE FROM rcirc_in_route" )
        for dd in self.insert_sql_list:
            sql = f"INSERT INTO rcirc_in_route (name, sec, min, free_sec) VALUES ('{dd['computer_name']}', {dd['busy_time_sec']}, {dd['busy_time_min']}, {dd['self_free_sec']})"
            try:
                cursor.execute( sql )
            except:
                self.logger.error ( f"BAD query: {sql} err: {sys.exc_info()[1]}" )
        cursor.close()


    #stage_2
    def save_rcirc_in_route_csv( self, path ):
        with open(path, 'w') as f:
            cursor = self.cnx.cursor()
            cursor.execute('select name, sec, min, free_sec from rcirc_in_route')
            f.write('name,sec,min,free_sec\n')
            for (name, sec, minut, free_sec) in cursor:
                f.write(f'{name},{sec},{minut},{free_sec}\n')
            cursor.close()
            f.close()


