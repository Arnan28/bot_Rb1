#pip install xlsxwriter
#pip install xlrd
#pip install xlrd==1.2.0

import ccxt
 
ftx = ccxt.ftx({
 'api_key': '.......................................', # API Keys
 'secret': '........................................'}) # API Secret
 
ftx.headers = {'FTX-SUBACCOUNT' : '...',}      # ถ้ามี เอา # ออกแล้วใส่ชื่อพอร์ต
 
import json
import pandas  
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import xlsxwriter
 
import time
 
token = '...........................................'  # Line token 
from songline import Sendline
messenger = Sendline(token)
 
def rebalance ():
 
  r = json.dumps ( ftx.fetch_ticker ( 'XRP/USD' ) )
  dataPrice = json.loads ( r )
  lastPrice = float ( dataPrice ['last'] )     #หากราคาเป็นจำนวนเต็ม ให้มาแก้ float เป็น int 
  #print(lastPrice)
 
  #markets = ftx.load_markets()
  #for market in markets:
  #print(market)
 
  #price = ftx.fetch_ticker('XRP/USD')['last']
  balance = ftx.fetchBalance()
 
  usd = balance['USD']['total']
  xrp = balance['XRP']['total']
  xrp_value = xrp * lastPrice
 
 
  timeframe = '5m'      # กำหนดกรอบเวลาที่ต้องการรัน 1m 5m 15m 1h 
  period = 20             # กำหนดค่าเฉลี่ยย้อนหลังกี่แท่งเทียน sma & ema
 
  ohlcv = ftx.fetch_ohlcv('XRP/USD',timeframe,None,period)
  d = json.dumps ( ohlcv )  
  data = pd.read_json ( d )#.tail(100)
  #print(data)

  #price = ftx.fetch_ticker('XRP/USD')['last']
  df = pd.DataFrame(ftx.fetchMyTrades('XRP/USD'),
                   columns=['datetime','symbol','side','price','amount','cost'])
  
  #ma = data[4].ewm(span=period).mean().tail(1)           #ema
  #print(f'ema : {ema}')
  
  ma = data[4].rolling(window=period).mean().tail(1)    #sma
  #print(f'sma : {sma}')
 
  std = data[4].rolling(window=period).std().tail(1)
  upper = ma + std * 3
  lower = ma - std * 3
                         
  #fix = 72                                            # จำนวน Asset Value ที่ต้องการกำหนด
  fix = ( xrp_value + usd ) / 2                # percenBalance จะเป็นการทำบาลานซ์ระหว่าง มูลค่าทรัพย์สินกับมูลค่าเงินสด สมการฟังก์ชั่นคือ y = x
  #percen = 1.2   
 

  if lastPrice < float (ma) or lastPrice > float (upper) and xrp_value > fix :   #หากราคาเป็นจำนวนเต็ม ให้มาแก้ float เป็น int 
    amount = xrp_value - fix
    bullet = amount//lastPrice
    
    if bullet < 1 :                    
          print( ' Ready Sell... ') 
          print( '               ')
          print( '               ')
    elif bullet >= 0 :  
          ftx.create_order('XRP/USD','market','sell',bullet)      
          v = bullet * lastPrice  
                     
          messenger.sendtext('Sell XRP %.2f' % v + 'USD @ ' + str (lastPrice)+'USD')   
                     
                   #สร้างตารางและดึงประวัติกำหนดคอลัม   
          df = pd.DataFrame(ftx.fetchMyTrades('XRP/USD'),
                   columns=['datetime','side','price','amount','cost'])      
                   
          sell = df.tail(1)  #ทำให้ประวัติเหลือบรรทัดสุดท้ายเพียง 1บรรทัด เพื่อนำข้อมูลไปใช้
          print(sell)          
                   #อ่านและบันทึกลง Excel  
          readDf = pd.read_excel(r'all.xlsx')
          frames = [readDf, sell]
          result = pd.concat(frames)
          writer = pd.ExcelWriter('all.xlsx', engine= 'xlsxwriter')
          result.to_excel(writer, sheet_name='all',header= True, index = False)
          writer.save()           

         
          

  elif lastPrice > float (ma) or lastPrice < float (lower) and xrp_value < fix :  #หากราคาเป็นจำนวนเต็ม ให้มาแก้ float เป็น int 
    amount = fix - xrp_value
    bullet = amount//lastPrice
    
    if bullet < 1 :
          print( ' Ready Buy... ') 
          print( '              ')
          print( '              ')        
    elif bullet >= 0 :
          ftx.create_order('XRP/USD','market','buy',bullet)      
          v = bullet * lastPrice 
          
          messenger.sendtext('Buy XRP %.2f' % v + 'USD @ ' + str (lastPrice)+'USD')   
              #อ่านและบันทึกลง Excel
          
          df = pd.DataFrame(ftx.fetchMyTrades('XRP/USD'),
                   columns=['datetime','side','price','amount','cost'])      
          
          buy = df.tail(1) 
          print(buy)          
          
          readDf = pd.read_excel(r'all.xlsx')
          frames = [readDf, buy]
          result = pd.concat(frames)
          writer = pd.ExcelWriter('all.xlsx', engine= 'xlsxwriter')
          result.to_excel(writer, sheet_name='all',header= True, index = False)
          writer.save()
           
  else :    
    
    print( '..Rb1prtbb...')
    print( '             ')
    print( '             ')


def report ():

 named_tuple = time.localtime() # get struct_time
 Time = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
 #print(Time) 
 
 balance = ftx.fetch_balance()

 price = ftx.fetch_ticker('XRP/USD')['last']
 df = pd.DataFrame(ftx.fetchMyTrades('XRP/USD'),
                   columns=['datetime','symbol','side','price','amount','cost'])

 xrp = balance['XRP']['total']
 usd = balance['USD']['total']
 xrp_value = xrp * price

 port_value = xrp_value + usd 

# %
 pa = (xrp_value / port_value) * 100
 pu = (usd / port_value) * 100

 dt = [['XRP',xrp,xrp_value,pa],['USD',usd,usd,pu]]
 cols = ['Asset','Amount','Value','    % Risk parity']
 ds = pd.DataFrame(dt,columns=cols)

 pt = [['XRP/USD',price],['Port Value',port_value]]
 pcols = ['Category','last']
 ps = pd.DataFrame(pt,columns=pcols)

 
 if xrp_value < usd or xrp_value > usd :
    print('                    ')     
    print('          Status Rb1                  ' + str (Time))    
    print(ps)
    print('                  ')   
    print('                  Risk parity Rb1')  
    print(ds)
    print('                    ')  
    print('                            Transection') 
    print(df.tail(5))
    print('                    ')  
    print(' Robot : percenBalance Bollinger Band Function  ')
    print('                    ')  
 else :
    print('Balance ')

while True:

    report()  
    
    rebalance()
    
    time.sleep(10)

#tf = '1h'
#pr = 20 
 
#ohlcvg = ftx.fetch_ohlcv('XRP/USD',tf)#,None,pr)
#dg = json.dumps ( ohlcvg )  
#datag = pd.read_json ( dg ).tail(200)
# print(data)
 
#sma = datag[4].rolling(window=pr).mean().tail(190)    #sma
#print(f'sma : {sma}')
 
#stdg = datag[4].rolling(window=pr).std()#.tail(190)
#upperg = sma + stdg * 3
#lowerg = sma - stdg * 3
 
#plt.figure(figsize = (12.5, 4.5))
#plt.plot(datag[4], label = 'XRPUSD')
#plt.plot(sma, label = 'sma')
#plt.plot(upperg, label = 'upper')
#plt.plot(lowerg, label = 'lower')

#ใช้เพื่อตรวจสอบว่าภายในโบรกเกอร์มีโปรดักส์อะไรบ้าง
#markets = ftx.load_markets()
#for market in markets:
# print(market)
