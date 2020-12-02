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
        #Построим калькуляторы скорости по описанию
        config_dict = cfg.get_computer_dict (config_file)
        comp_list = cmptr.create_computers( config_dict, logger, db_conn )
        logger.info(f"Загружены калькураторы скорости: {', '.join(e.name() for e in comp_list)}")

        #Запуским расчет скорости и сохранение данных в БД
        db_conn.handle_signals( cmptr.create_ts_names( comp_list ), comp_list )
        #Проверим что все калькуляторы корректно отработали
        cmptr.check_states( comp_list, logger )

    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')

#    except Exception as e:
#        logger.error(e)

if __name__ == '__main__':
    main()
