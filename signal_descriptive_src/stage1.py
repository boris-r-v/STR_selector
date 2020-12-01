# -*- coding: utf-8 -*-

import mysql_selector as mysql_selector
import descriptive_statistics as ds

import config as cfg
import logging,csv,sys,os


logger = logging.getLogger("Selector")

config_file = "./config.yml"

def main():
    try:
        logger.info(os.getcwd())

        db_conn = mysql_selector.MysqlSelector( logger, config_file ) #sys.argv[1] )
        ts_list = cfg.get_entry_signal_data( config_file ).split(',') 
        logger.info("Запрошен сбор статистики по ТС: {} ТС входных сигналов".format(ts_list))
        ds.describe_ts( ts_list, db_conn, logger )


        ts_list = cfg.get_sail_signal_data( config_file ).split(',') 
        logger.info("Запрошен сбор статистики по ТС: {} ТС выходных сигналов".format(ts_list))
        ds.describe_ts( ts_list, db_conn, logger )

        ts_list = cfg.get_rcirc_signal_data( config_file ).split(',') 
        logger.info("Запрошен сбор статистики по ТС: {} ТС секций".format(ts_list))
        ds.describe_ts( ts_list, db_conn, logger )

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')

#    except Exception as e:
#        logger.error(e)

if __name__ == '__main__':
    main()
