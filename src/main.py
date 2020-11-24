# -*- coding: utf-8 -*-

import mysql_selector as mysql_selector
import descriptive_statistics as ds

import config as cfg
import logging,csv,sys,os


logger = logging.getLogger("Selector")

def main():
    try:
        logger.info(os.getcwd())

        db_conn = mysql_selector.MysqlSelector( logger, "./config.ini" ) #sys.argv[1] )
        ts_list = cfg.get_signal_data( "./config.ini" ).split(',') 
        logger.info("Запрошены проверка ТС: {}".format(ts_list))

        ds.describe_ts( ts_list, db_conn, logger )

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')

#    except Exception as e:
#        logger.error(e)

if __name__ == '__main__':
    main()
