# -*- coding: utf-8 -*-

import configparser
import unittest as ut

class ConfigKeyNotExist(Exception):
    pass

def throw( ex_str ):
    raise ConfigKeyNotExist( ex_str )

def get_entry_signal_data( cfile ):
    """
    Возвращает уровень логинга
    Если ключ не найден генерируется исключение ConfigKeyNotExist

    :param cfile - путь к конфигурационному файлу
    """
    config = configparser.ConfigParser()
    config.read( cfile )
    return config["STAGE1"]["ENTRY_TS"]

def get_sail_signal_data( cfile ):
    """
    Возвращает уровень логинга
    Если ключ не найден генерируется исключение ConfigKeyNotExist

    :param cfile - путь к конфигурационному файлу
    """
    config = configparser.ConfigParser()
    config.read( cfile )
    return config["STAGE1"]["SAIL_TS"]

def get_rcirc_signal_data( cfile ):
    """
    Возвращает уровень логинга
    Если ключ не найден генерируется исключение ConfigKeyNotExist

    :param cfile - путь к конфигурационному файлу
    """
    config = configparser.ConfigParser()
    config.read( cfile )
    return config["STAGE1"]["RCIRC_TS"]

def get_mysql_server_config( cfile ):
    """
    ---Возвращает dict {"ip":"mysq_server_ip", "db":"db_name", "user":"db_user" } конфигурации по ключу заданному в атрибуте secrion
    Возвращает tuple [mysq_server_ip, db_name, db_user ] конфигурации по ключу заданному в атрибуте secrion
    Если ключ не найден генерируется исключение ConfigKeyNotExist

    :param cfile - путь к конфигурационному файлу
    :param section - секция для которой получить конфигурацию, доступны [DATA_SOURCE|DATA_CLEANER|DATA_MINER|NOTIFIER]

    """
    section = "MYSQL"
    config = configparser.ConfigParser()
    config.read( cfile )
    if ( section in config ):
        sect = config[section]
        if ( "IP" in sect and "DATABASE" in sect and "USER" in sect):
            return [ sect["IP"], sect["DATABASE"], sect["USER"] ]#{"ip":sect["IP"], "db":sect["DATABASE"], "user":sect["USER"] }
        else:
            throw( f"IP or DATABSE or USER section not exist in {section} in config file {cfile}" )
    else:
        throw( f"{section} section not exist in config file {cfile}" )


def get_logger_level( cfile ):
    """
    Возвращает уровень логинга
    Если ключ не найден генерируется исключение ConfigKeyNotExist

    :param cfile - путь к конфигурационному файлу
    """
    config = configparser.ConfigParser()
    config.read( cfile )
    return config["DEFAULT"]["LOGGER_LEVEL"]


class Tester( ut.TestCase ):

    def test_correct_config_data( self ):
        ip, db, user = get_mysql_server_config("./config.ini")
        self.assertEqual( ip, '172.12.0.2' )
        self.assertEqual( db, "doppler_muslumovo" )
        self.assertEqual( user, "disp" )


#    def test_incorrect_config_data( self ):
#        with self.assertRaises(ConfigKeyNotExist) as cm:
#           ip, port, timeout = get_server_config("./director.ini", "DATA_SRC")
#        self.assertEqual ("DATA_SRC section not exist in config file ./director.ini", str(cm.exception))

    def test_get_logger_level( self ):
        level = get_logger_level( "./config.ini" )
        self.assertEqual ("INFO", level )

    def test_get_signal( self ):
        ts = get_signal_data( "./config.ini" )
        self.assertEqual ("Ч(з),Н(з)", ts )

if __name__ == '__main__':
    ut.main()

