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

        db_conn = mysql_selector.MysqlSelector( logger, config_file )
        rcirc_mask = cfg.get_rcirc_mask_and_active_state( config_file )
        print ( rcirc_mask )

        rcirc_decrip = db_conn.select_decriptive_statictics( rcirc_mask['zIn'] )
        print ( rcirc_decrip )
        df = ds.st2_create_bunch_from_dict ( rcirc_decrip )
        print ( df )

#        print ( type(df['1-9СП(к)']['0']) )

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')

#    except Exception as e:
#        logger.error(e)

if __name__ == '__main__':
    main()
