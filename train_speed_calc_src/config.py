# -*- coding: utf-8 -*-

import yaml
import unittest as ut

class ConfigKeyNotExist(Exception):
    pass

def throw( ex_str ):
    raise ConfigKeyNotExist( ex_str )

def get_computer_dict( cfile ):
    with open( cfile ) as c:
        config = yaml.full_load(c)
        return config["COMPUTE"]["OBJECTS"]
    throw (f"Нет указанного файла конфигурации r{cfile}")

def get_mysql_server_config( cfile ):
    """
    ---Возвращает dict {"ip":"mysq_server_ip", "db":"db_name", "user":"db_user" } конфигурации по ключу заданному в атрибуте secrion
    Возвращает tuple [mysq_server_ip, db_name, db_user ] конфигурации по ключу заданному в атрибуте secrion
    Если ключ не найден генерируется исключение ConfigKeyNotExist

    :param cfile - путь к конфигурационному файлу
    :param section - секция для которой получить конфигурацию, доступны [DATA_SOURCE|DATA_CLEANER|DATA_MINER|NOTIFIER]

    """
    section = "MYSQL"
    c = open( cfile )
    config = yaml.full_load(c)
    if ( section in config ):
        sect = config[section]
        if ( "IP" in sect and "DATABASE" in sect and "USER" in sect):
            return [ sect["IP"], sect["DATABASE"], sect["USER"] ]#{"ip":sect["IP"], "db":sect["DATABASE"], "user":sect["USER"] }
        else:
            throw( f"IP or DATABSE or USER section not exist in {section} in config file {cfile}" )
    else:
        throw( f"{section} section not exist in config file {cfile}" )
