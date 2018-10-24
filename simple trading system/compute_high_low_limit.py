# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 22:41:42 2018

@author: kite
"""
import datetime
from pymongo import UpdateOne, ASCENDING
from database import DB_CONN
from stock_util import get_trading_dates, get_all_codes
import numpy as np
import pandas as pd
import requests
import json

"""
计算涨跌停价格

只要获取到前一天的价格

获取name和上市日期

最新ipo规则
如果是上市当天，则涨停价是上市发行价格的1.44倍
所以需要获取到发行价格
要不是
"""

# %% 获取发行价格并保存到数据库中

Sess = requests.Session()
agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
headers = {'User-Agent':agent}
url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=XGSG_LB&token=70f12f2f4f091e459a279469fe49eca5&st=listingdate,securitycode&sr=-1&p={page}&ps=2000&js={"pages":(tp),"data":(x)}'
html = Sess.get(url, headers=headers)
result = json.loads(html.text)
df = pd.DataFrame(result['data'])
df = df.set_index('securitycode')
doc_issueprice = dict(df.loc[:,'issueprice'])

codes = doc_issueprice.keys()
update_requests = []

for code in codes:
    basic = DB_CONN['basic'].find({'code':code},
                   projection={'code':True, '_id':False})
    result = [b for b in basic]
    if len(result)>0:
        update_requests.append(
            UpdateOne(
                {'code':code},
                {'$set':{'issueprice':doc_issueprice[code]}},
                upsert=True))
        
if len(update_requests)>0:
    update_result = DB_CONN['basic'].bulk_write(update_requests, ordered=False)
    print('填充字段， 字段名: issueprice，数据集：%s，插入：%4d条，更新：%4d条' %
              ('basic', update_result.upserted_count, update_result.modified_count), flush=True)


#for _date in trade_dates:
#    result = [b for b in basic.find({'timeToMarket':_date}, projection = {'code':True, 'date':True, 'timeToMarket':True, '_id':False})]
#    if len(result) > 0:
#        break
    
# %% 
"""
st_mark = ['st', 'ST', '*st', '*ST']

好，现在有发行价格了

开始计算涨跌停价格

按单天来算

先获取日期内的交易日

对交易日进行循环，按照每一个交易日

    填充所有股票的单个交易日涨跌停价格

def  填充所有股票的单个交易日涨跌停价格
    
    for code in codes:

        获取该股票在这个交易日下的名字,发行日期， 233, 没有存名字！！！
        
        if 该股票的发行日期和当前日期相同，再获取该股票的发行价格，正常来说，是应该能获取得到:
    
            high_limit = np.round(np.round(issueprice * 1.2, 2) * 1.2, 2)
            low_limit = np.round(np.round(issueprice * 0.8, 2) * 0.8, 2)
            
        elif 如果股票的名字中前两位是st 或者 前 3位是 *st:
            high_limit = np.round(pre_close * 1.05, 2)
            low_limit = np.round(pre_close * 0.95， 2)
        else:
            high_limit = np.round(pre_close * 1.1, 2)
            low_limit = np.round(pre_close * 0.9， 2)
            
        将数据填充到
        
"""    