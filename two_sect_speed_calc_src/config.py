# - *- coding: utf-8 -*-

import yaml
import logging
import unittest as ut

class ConfigKeyNotExist(Exception):
    pass

def throw( ex_str ):
    raise ConfigKeyNotExist( ex_str )

def get_computers_config( cfile ):
    with open( cfile ) as c:
        config = yaml.full_load(c)
        return (config["COMPUTE"]["OBJECTS"],  config["COMPUTE"]["ANOMALY_SPEED"], config["COMPUTE"]["LOG_FILE"] )

def get_mysql_server_config( cfile ):
    """
    ---Возвращает dict {"ip":"mysq_server_ip", "db":"db_name", "user":"db_user" } конфигурации по ключу заданному в атрибуте secrion
    Возвращает tuple [mysq_server_ip, db_name, db_user ] конфигурации по ключу заданному в атрибуте secrion
    Если ключ не найден генерируется исключение ConfigKeyNotExist

    :param cfile - путь к конфигурационному файлу
    :param section - секция для которой получить конфигурацию, доступны [DATA_SOURCE|DATA_CLEANER|DATA_MINER|NOTIFIER]

    """
    c = open( cfile )
    config = yaml.full_load(c)
    sect = config['MAIN']['MYSQL']
    if ( "IP" in sect and "DATABASE" in sect and "USER" in sect):
        return [ sect["IP"], sect["DATABASE"], sect["USER"] ]#{"ip":sect["IP"], "db":sect["DATABASE"], "user":sect["USER"] }
    else:
        throw( f"IP or DATABSE or USER section not exist in {section} in config file {cfile}" )


def set_loggin_level( cfile, logger ):
    with open( cfile ) as c:
        config = yaml.full_load(c)
        log_level = config["MAIN"]["LOG_LEVEL"]
        if ( "INFO" == log_level ):
            logging.basicConfig(level = logging.INFO)
        elif ( "DEBUG" == log_level ):
            logging.basicConfig(level = logging.DEBUG)
        elif ( "WARNING" == log_level ):
            logging.basicConfig(level = logging.WARNING)
        elif ( "ERROR" == log_level ):
            logging.basicConfig(level = logging.ERROR)
        elif ( "CRITICAL" == log_level ):
            logging.basicConfig(level = logging.CRITICAL)
        """
        if ( "INFO" == log_level ):
            logger.setLevel( logging.INFO )
        elif ( "DEBUG" == log_level ):
            logger.setLevel( logging.DEBUG )
        elif ( "WARNING" == log_level ):
            logger.setLevel( logging.WARNING )
        elif ( "ERROR" == log_level ):
            logger.setLevel( logging.ERROR )
        elif ( "CRITICAL" == log_level ):
            logger.setLevel( logging.CRITICAL )

        """








