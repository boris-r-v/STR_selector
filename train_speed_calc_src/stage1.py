# -*- coding: utf-8 -*-

import mysql_selector as mdbc
import config as cfg
import computer as cmptr


import logging,csv,sys,os


logger = logging.getLogger("Selector")
config_file = "./config.yml"

def main():
    try:
        logger.info(os.getcwd())

        config_dict = cfg.get_computer_dict (config_file)
        comp_list = cmptr.create_computers( config_dict )

        db_conn = mdbc.MysqlSelector( logger, config_file )
        ts_list = db_conn.create_ts_list( cmptr.create_ts_names( comp_list ) )

        for ts in ts_list:
            for comp in comp_list:
                comp.new_state( ts )

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')

#    except Exception as e:
#        logger.error(e)

if __name__ == '__main__':
    main()
