# -*- coding: utf-8 -*-

import mysql_selector as mysql_selector
import data_handler as dh

import config as cfg
import logging,csv,sys,os


logger = logging.getLogger("Selector")

def main():
    try:
        logger.info(os.getcwd())

        selector = mysql_selector.MysqlSelector( logger, "./config.ini" ) #sys.argv[1] )
        ts_list = cfg.get_signal_data( "./config.ini" ).split(',') 
        logger.info("Запрошены проверка ТС: {}".format(ts_list))

        for ts_name in ts_list:
             dh.write_dict_to_cvs( dh.from_ts_state_to_time_interval( selector.get_data_from_ts(ts_name=ts_name, limit=1000000) ), ts_name, logger)

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')

#    except Exception as e:
#        logger.error(e)

if __name__ == '__main__':
    main()
