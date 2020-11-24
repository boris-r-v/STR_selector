# -*- coding: utf-8 -*-

import config as cfg
import datetime as dt
import mysql.connector
import json
import logging

logging.basicConfig(level = logging.INFO)

class MysqlSelector(object):
    def __init__( self, logger, config_file ):
        self.logger = logger

        ip, db, user = cfg.get_mysql_server_config( config_file )
        logger.info("MySQL config: 'ip':'{}', 'db':'{}', 'user':'{}'".format(ip, db, user) )
        self.cnx = mysql.connector.connect( user=user, database=db, host=ip )
        logger.info("MySQL connected".format() )
        cursor = self.cnx.cursor()
        cursor.execute( "SET NAMES 'latin1'" )


    def get_data_from_ts( self, ts_name, limit ):
        sql_req= u"select from_unixtime(sec) as time, sec, who, value from loglist where kind='Импульс.ТЗК' and who IN ('{}') limit {:d}".format(ts_name, limit)
        return self.query( sql_req )


    def query( self, sql_str ):
        cursor = self.cnx.cursor()
        cursor.execute( sql_str )

        lst = []
        for (time, sec, who, value) in cursor:
            lst.append( [ sec, who, "0" if value.find("пассивен") != -1 else "1" ] )
        cursor.close()
        return lst



