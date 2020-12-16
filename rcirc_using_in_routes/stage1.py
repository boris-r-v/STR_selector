# -*- coding: utf-8 -*-

import mysql_selector as mdbc
import config as cfg
import computer as clc

import logging,csv,sys,os


logger = logging.getLogger("Selector")

config_file = "./config.yml"

def main():
    try:
        #Выясним какой у нас конфиг
        cngfile = config_file if( 1 == len(sys.argv) ) else sys.argv[1]
        #Установил уровень логгирования
        cfg.set_loggin_level( cngfile, logger )
        #Подключимся к БД
        db_conn = mdbc.MysqlSelector( logger, cngfile )
        #Создадим калькуляторы
        cmp_list = clc.create_computers( cfg.get_computers_config( cngfile ), logger, db_conn )
        #Получим список ТСов которые учавствуют в расчете
        ts_list = clc.create_ts_names( cmp_list )
        print (ts_list)
        #Запустим расчет
        db_conn.handle_ts_signals( ts_list, cmp_list )

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')

#    except Exception as e:
#        logger.error(e)

if __name__ == '__main__':
    main()
