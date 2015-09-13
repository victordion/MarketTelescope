import datetime
import urllib2
import csv
import numpy
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

def getMarketDataToCVS(symbol):
    assert type(symbol) is str
   
    '''
    Yahoo finance API assumes month index start from 0 instead of 1
    '''

    from_date_d = 1
    from_date_m = 0
    from_data_y = 1970

    now = datetime.datetime.now()
    to_date_d = now.day
    to_date_m = now.month - 1
    to_date_y = now.year


    url = 'http://ichart.yahoo.com/table.csv?s={0}&a={1}&b={2}&c={3}&d={4}&e={5}&f={6}&g=d&ignore=.csv'.\
            format(symbol, from_date_m, from_date_d, from_data_y, to_date_m, to_date_d, to_date_y)

    response = urllib2.urlopen(url)
    content = response.read()
    content = content.split('\n')
    data = csv.reader(content)
    return list(data)


def getDatePriceMap(data1, data2, num_days = 20, days_before_today = 0 ):
    dates = []
    price1 = []
    price2 = []
    idx1 = 1
    idx2 = 1
    end_date = datetime.datetime.now() -  datetime.timedelta(days=days_before_today)

    while end_date < datetime.datetime.strptime(data1[idx1][0], '%Y-%m-%d'):
        idx1 += 1
    while end_date < datetime.datetime.strptime(data2[idx2][0], '%Y-%m-%d'):
        idx2 += 1

    while num_days > 0:
        date1 = datetime.datetime.strptime(data1[idx1][0], '%Y-%m-%d') 
        date2 = datetime.datetime.strptime(data2[idx2][0], '%Y-%m-%d')
        
        if date1 == date2:
            dates.append(data1[idx1][0])
            price1.append(float(data1[idx1][-1]))
            price2.append(float(data2[idx2][-1]))
            idx1 += 1
            idx2 += 1
            num_days -= 1
        
        elif date1 > date2:
            idx1 += 1
        else:
            idx2 += 1
     
    corr = numpy.corrcoef(price1, price2)[0, 1]

    return end_date.strftime('%m-%d-%Y'), corr


def getCorr(symbol1, symbol2, window_len, days_offset):
    data1 = getMarketDataToCVS(symbol1)
    data2 = getMarketDataToCVS(symbol2)
    date_list = []
    corr_list = []
    for i in range(0, days_offset):
        print 'Computing window_len ' + str(window_len) + ' days back for ' + str(i) + ' days'
        d, c =  getDatePriceMap(data1, data2, window_len, i)
        date_list.append(d)
        corr_list.append(c)
    return date_list, corr_list

def plotCorr(symbol1, symbol2):
    span = 2000
    dates, y_10 = getCorr(symbol1, symbol2, 10, span)
    dates, y_20 = getCorr(symbol1, symbol2, 20, span)
    dates, y_30 = getCorr(symbol1, symbol2, 30, span)
    dates, y_40 = getCorr(symbol1, symbol2, 40, span)
    
    print dates
    x = [datetime.datetime.strptime(d,'%m-%d-%Y').date() for d in dates]
    #print x, y

    fig = plt.figure()
    fig.set_size_inches(150, 10)
    fig.suptitle('Stock price of ' + symbol1 + ' and ' + symbol2, fontsize=14, fontweight='bold')
    b_patch = mpatches.Patch(color='b', label='10 day')
    r_patch = mpatches.Patch(color='r', label='20 day')
    g_patch = mpatches.Patch(color='g', label='30 day')
    c_patch = mpatches.Patch(color='c', label='40 day')
    plt.legend(handles=[b_patch, r_patch, g_patch, c_patch])

    plt.plot(x, y_10, 'b--', x, y_20, 'r--', x, y_30, 'g--', x, y_40, 'c--')
    plt.setp(plt.gca().xaxis.get_majorticklabels(),rotation=90) 
    plt.plot(x, y_10, 'b--', x, y_20, 'r--', x, y_30, 'g--', x, y_40, 'c--')
    plt.setp(plt.gca().xaxis.get_majorticklabels(),rotation=90) 
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=span/10))
    
    plt.gcf().autofmt_xdate()
    plt.savefig('stock_corr.png', dpi = 200)
    #plt.show()

#plotCorr('AMZN', 'MSFT')
#plotCorr('AMZN', 'TXN')
