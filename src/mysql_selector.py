# -*- coding: utf-8 -*-

import config as cfg
import datetime as dt
import mysql.connector
import json
import logging

logging.basicConfig(level = logging.INFO)
create_statistics_table="CREATE TABLE IF NOT EXISTS descriptive_statistics (ts_name VARCHAR(30), state SMALLINT, mean FLOAT, std FLOAT, first_quantile FLOAT, median FLOAT, third_quantile FLOAT, min FLOAT, max FLOAT, PRIMARY KEY(ts_name, state) ) ENGINE=MYISAM "

class MysqlSelector(object):
    def __init__( self, logger, config_file ):
        self.logger = logger

        ip, db, user = cfg.get_mysql_server_config( config_file )
        logger.info("MySQL config: 'ip':'{}', 'db':'{}', 'user':'{}'".format(ip, db, user) )
        self.cnx = mysql.connector.connect( user=user, database=db, host=ip )
        logger.info("MySQL connected".format() )
        cursor = self.cnx.cursor()
        cursor.execute( "SET NAMES 'latin1'" )
        cursor.execute( create_statistics_table )


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
            qu = f"REPLACE INTO descriptive_statistics (ts_name, state, mean, std, first_quantile, median, third_quantile, min, max) VALUES ('{ts_name}', {int(i)}, {descrip[i]['mean']}, {descrip[i]['std']}, {descrip[i]['25%']}, {descrip[i]['50%']}, {descrip[i]['75%']}, {descrip[i]['min']}, {descrip[i]['max']} )"
            try:
                cursor.execute( qu )
            except:
                self.logger.error ( f"BAD query: {qu}" )
                print (descrip[i])