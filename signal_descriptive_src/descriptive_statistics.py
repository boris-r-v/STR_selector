# -*- coding: utf-8 -*-

import pandas as pd
import mysql_selector as sql_selector
import matplotlib.pyplot as plt
import ts_series_to_time_interval as dh
import math

from sklearn.utils import Bunch
import numpy

mb = Bunch()
mb.zero_data=numpy.ndarray([1,2,2,2,2], dtype=float)
mb.one_data=[4,4,4,4,4]
mb.name = ['1','2','3','4','5']
mb.features = ['mean', 'std' ]
type(mb.zero_data)


def st2_create_bunch_from_dict ( in_dict ):

    key_list = []
    one_state_list = []
    zero_state_list = []
    name_features = ['mean', 'std', 'min' '25%', '50%', '75%', 'max']
    for key in in_dict.keys():
        n_zero = [ in_dict[key]['0']['mean'], in_dict[key]['0']['std'], in_dict[key]['0']['min'], in_dict[key]['0']['25%'], in_dict[key]['0']['50%'], in_dict[key]['0']['75%'], in_dict[key]['0']['max'] ]
        n_one = [ in_dict[key]['1']['mean'], in_dict[key]['1']['std'], in_dict[key]['1']['min'], in_dict[key]['1']['25%'], in_dict[key]['1']['50%'], in_dict[key]['1']['75%'], in_dict[key]['1']['max'] ]

        key_list.append(key)
        one_state_list.append(n_one)
        zero_state_list.append(n_zero)

    mb = Bunch()
    mb.zero_data = numpy.array(zero_state_list, dtype=float)
    mb.one_data = numpy.array(one_state_list, dtype=float)
    mb.name = key_list
    mb.features = name_features
    return mb

def create_dataframe_from_dict( in_dict ):

    df = pd.DataFrame( in_dict )
    for key in in_dict.keys():
        med = df[key].quantile(0.5)
        df[key] = df[key].fillna(med)
    return df



def change_outliers_to_median_into_series ( series: pd.Series ):
    """
        Change outliers into pandas series, to a median value
    """
    first_quantile = series.quantile(0.25)
    median = series.quantile(0.5)
    third_quantile = series.quantile(0.75)
    IQR = third_quantile - first_quantile
    hight_outliers_border = third_quantile + 1.5 * IQR
    bottom_outliers_border = first_quantile - 1.5 * IQR

    ns = series.copy()
    ns = ns.transform( lambda x: x if ( x > bottom_outliers_border and x < hight_outliers_border ) else median )
    return ns

def change_outliers_to_median_into_dataframe( df: pd.DataFrame, keys: list ):
    """
        Change outliers into pandas dataframe, to a median value
    """
    npd = pd.DataFrame()
    for key in keys:
        npd = npd.join( change_outliers_to_median_into_series ( df[ key ] ), how='right' )
    return npd


def draw_plot(dfs, titles, logger ):
    if ( len(dfs) != len(titles) ):
        logger.info("Размеры спика данных и списка подписей не совпадают")
        return

    fig, axs = plt.subplots(2, 2)
    axs[0,0].boxplot(dfs[0]['0'])
    axs[0,0].set_title(titles[0]+' 0')

    axs[0,1].boxplot(dfs[0]['1'])
    axs[0,1].set_title(titles[0]+' 1')

    axs[1,0].boxplot(dfs[1]['0'])
    axs[1,0].set_title(titles[1]+' 0')

    axs[1,1].boxplot(dfs[1]['1'])
    axs[1,1].set_title(titles[1]+' 1')

#    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.05, top=0.9, hspace=0.4, wspace=0.3)

    plt.show()

    fig, axs = plt.subplots(2, 2)
    axs[0,0].hist(dfs[0]['0'])
    axs[0,0].set_title(titles[0]+' 0')

    axs[0,1].hist(dfs[0]['1'])
    axs[0,1].set_title(titles[0]+' 1')

    axs[1,0].hist(dfs[1]['0'])
    axs[1,0].set_title(titles[1]+' 0')

    axs[1,1].hist(dfs[1]['1'])
    axs[1,1].set_title(titles[1]+' 1')

#    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.05, top=0.9, hspace=0.4, wspace=0.3)

    plt.show()

def describe_ts( ts_list, db_conn, logger ):
    """
        Create statistic decriptions for ts states, and save in to file
    """
    for ts_name in ts_list:
        logger.info("\tОбработка импульса ТС: {}".format(ts_name))
        pd_df = create_dataframe_from_dict( dh.from_ts_state_to_time_interval( db_conn.get_data_from_ts(ts_name=ts_name, limit=1000000), ts_name ) )
        db_conn.store_decriptive_staticsics(pd_df.describe(), ts_name )

        #df_wo = change_outliers_to_median_into_dataframe( pd_df, ['0', '1'] )
        #print( ts_name,"\n", pd_df )
        #print( ts_name,"\n", pd_df.describe())
        #print( ts_name,"-wo\n", df_wo )
        #print( ts_name," очищенная\n", df_wo.describe() )
        #draw_plot([pd_df, df_wo], ["Outliers", "No outliers"], logger )

