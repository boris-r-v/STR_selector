# -*- coding: utf-8 -*-

import mysql_selector as mdbc
import config as cfg
import computer as cmptr


import logging,csv,sys,os


logger = logging.getLogger("TrainSpeed")

config_file = "./config.yml"

def main():
    try:
        #Установил уровень логгирования
        cfg.set_loggin_level( config_file, logger )
        #Подключимся к БД
        db_conn = mdbc.MysqlSelector( logger, config_file )

        db_conn.save_rcirc_in_route_csv('./rcirc_in_route.csv')

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')

#    except Exception as e:
#        logger.error(e)

if __name__ == '__main__':
    main()
