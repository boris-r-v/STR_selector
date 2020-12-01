# -*- coding: utf-8 -*-

import config as cfg
import datetime as dt
import mysql.connector
import json
import logging

logging.basicConfig(level = logging.INFO)
create_statistics_table="CREATE TABLE IF NOT EXISTS descriptive_statistics (ts_name VARCHAR(30), state VARCHAR(10), mean FLOAT, std FLOAT, first_quantile FLOAT, median FLOAT, third_quantile FLOAT, min FLOAT, max FLOAT, PRIMARY KEY(ts_name, state) ) ENGINE=MYISAM "

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

