import os
from shutil import copyfile

os.chdir('/home/victor/codebase/MarketTelescope/')
src = 'stock_corr.png'
dst = '/var/www/html/market_telescope/stock_corr.png'
os.system("python ./getMarket.py")
copyfile(src, dst)
