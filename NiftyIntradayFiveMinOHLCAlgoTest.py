import csv, math, statistics, datetime, json, datetime, re, array
import sys
sys.path.append(r"C:\Users\keyur\Documents\Keyur\TradeBook\PythonPrograms")

import OptionsPriceCalculator as optionPCalc

'''
Nifty straddle test based on 5min OHLC data.

read 5 min OHLC data for a day.
Collect data for a day and
Attach OpenIV data from VIX file. PE IV same, CE IV (-2) for ATM options.
(IV used from India VIX index data)
Algo for entry exit.

100 points algo.
if gap is > 90
45 points retracement after 85 points from open/low/high of 1st candle. SL 25 points.
if gap < 90, 60 points retracement after 125 points from open/high/low of 1st candle. SL 25 points.

retracement 2nd destination 100 points or close PP
or SL as entry point.

how to traverse:
take 1st candle open, high, low.
from 2nd candle onwards check current-high to 1st-open or 1st-low diff and check for threashold.
If breached mark entry point as current-high for PE entry.
Mark target as 45 points retracement and SL as entry + 25 points.

Traverse next candles and check if either Target hit for next low or SL hit for next high.
If either hit calculate +ve or -ve Pnl.
Mark day as complete and move to next day.
If no target or SL hit, at 3.10 candle Close PP, exit.
calculate +ve or -ve Pnl.
Mark day as complete and move to next day.

calculate final Pnl for the day.
calculate extra pnl for the day.

Version_1: complete for above points.
Date: 21-Jul-2022

'''

class NiftyIntradayFiveMinOHLCAlgoTest:

    iv_data_ary = []
    #this is an map with key as date
    #and value 2D array, 1st element array of 5min OHLC for the day, 2nd elem is IV.
    daily_data_dict = dict()
    index_data_ary = []
    all_data = []
    opInst = None
    pnl_strategy = 1
    debug_flag = 0
    slippage_txn_cost = 1
    retracement = 45
    threshold = 85
    SL_threshold = 25
    extra_retr = 45
    #1. 300 points ITM strikes 
    strikes_choose_logic = 1
    tradeLogsCapture = dict()
    strike_rate = 0
    
    def writeTradeLog(self, cur_date, argsAry):
        if(cur_date not in self.tradeLogsCapture):
            self.tradeLogsCapture[cur_date] = []

        (self.tradeLogsCapture[cur_date]).append(argsAry)   
       

    def writeTradeLogsToFile(self):
         with open('C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\data\\hist\\NiftyIntradayFiveMinOHLCAlgoTestLogs.csv',
                  'w', newline='') as csvfile:
            csvTradeLogsWriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for datekey in self.tradeLogsCapture:
                dateary = self.tradeLogsCapture[datekey]
                csvTradeLogsWriter.writerow(dateary)
            
        
    def readIVDataFile(self, fileName):    
        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            self.iv_data_ary = list(reader)
            del self.iv_data_ary[0]
            i = 0
            while i < 2:
                print(self.iv_data_ary[i])
                i = i + 1

    def readOHLCDataFile(self, fileName):

        ohlcjason = None
        with open(fileName, 'r') as f:
            ohlcjason = json.load(f)

        self.all_data = ohlcjason ['candles']
        datalen = len(self.all_data)
        i = 0
        latest_date = ''
        while i < datalen:
            
            cur_date_str = self.all_data[i][0] 
            cur_date_str = cur_date_str[0:10]
            if(latest_date != cur_date_str):
                
                #new date data started                
                self.daily_data_dict[cur_date_str] = []
                latest_date = cur_date_str
                
            (self.daily_data_dict[cur_date_str]).append(self.all_data[i])
            #print(self.all_data[i])
            i = i + 1

        #print(self.daily_data_dict)

    def backTestStrategy(self):
        # merge data
        cum_pnl = 0
        idx = 0
        for datekey in self.daily_data_dict:
            dateary = self.daily_data_dict[datekey]
            final_pnl = self.calculateStrikesAndPremAndPnl(self, datekey, dateary, idx)            
            cum_pnl = cum_pnl + (final_pnl - self.slippage_txn_cost)
            idx = idx + 1
        
        self.writeTradeLogsToFile(self)
        print('datalen', idx, 'cum_pnl', cum_pnl, 'strikes_rate', self.strike_rate)
    
    def calculateStrikesAndPremAndPnl(self, datekey, dateary, idx):
        #print(dateary)
        cur_date = datekey
        iv_date = self.iv_data_ary[idx][0]
        cur_date_format = "%Y-%m-%d"
        iv_date_format = "%d-%b-%Y"
        cur_dt_object = datetime.datetime.strptime(cur_date, cur_date_format)
        iv_dt_object = datetime.datetime.strptime(iv_date, iv_date_format)
        if (cur_dt_object != iv_dt_object):
            print(cur_date, 'Date not matching', iv_date)
            return 0
        day = cur_dt_object.weekday()
        dayToExp = self.dayToExpiry(self, day)
        
        cur_iv = float(self.iv_data_ary[idx][1])
        close_iv = float(self.iv_data_ary[idx][4])

        openP_1c = math.floor(float(dateary[0][1]))
        highP_1c = math.floor(float(dateary[0][2]))
        lowP_1c = math.floor(float(dateary[0][3]))
        datalen = len(dateary)
        dayCloseP = math.floor(float(dateary[datalen-1][1])) # last candle open PP

        PE_entry_point = lowP_1c + self.threshold
        CE_entry_point = highP_1c - self.threshold
        
        PE_tgt_point = PE_entry_point - self.retracement
        CE_tgt_point = CE_entry_point + self.retracement

        PE_SL_point = PE_entry_point + self.SL_threshold
        CE_SL_point = CE_entry_point - self.SL_threshold
                
        PE_Strike = 0
        CE_Strike = 0
        base = round(openP_1c, -2)
        IV_extra = 0
        #300 ITM logic
        if(self.strikes_choose_logic == 1):            
            PE_Strike = base +300
            CE_Strike = base -300

        cur_iv = cur_iv +IV_extra

        self.writeTradeLog(self, cur_date, ['openP_1c', openP_1c, dayCloseP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp])
        #print(cur_date, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp)
        CE_entry_pp = self.opInst.calcPrem(self.opInst, CE_entry_point, CE_Strike, dayToExp-0.1, cur_iv-1, 'CE')
        PE_entry_pp = self.opInst.calcPrem(self.opInst, PE_entry_point, PE_Strike, dayToExp-0.1, cur_iv, 'PE')

        CE_tgt_pp = self.opInst.calcPrem(self.opInst, CE_tgt_point, CE_Strike, dayToExp-0.5, cur_iv-1, 'CE')
        PE_tgt_pp = self.opInst.calcPrem(self.opInst, PE_tgt_point, PE_Strike, dayToExp-0.5, cur_iv, 'PE')

        CE_SL_pp = self.opInst.calcPrem(self.opInst, CE_SL_point, CE_Strike, dayToExp-0.5, cur_iv-1, 'CE')
        PE_SL_pp = self.opInst.calcPrem(self.opInst, PE_SL_point, PE_Strike, dayToExp-0.5, cur_iv, 'PE')
        self.writeTradeLog(self, cur_date, [CE_entry_point, CE_tgt_point,  CE_SL_point, PE_entry_point, PE_tgt_point, PE_SL_point ])
        self.writeTradeLog(self, cur_date, [CE_entry_pp,  CE_tgt_pp, CE_SL_pp,  PE_entry_pp, PE_tgt_pp, PE_SL_pp])
        #print(cur_date, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)
        
        final_pnl = 0
        
        if(self.pnl_strategy >= 1):
            trade_flag = self.retrAlgoStrategy(self, cur_date, cur_dt_object, CE_entry_point, PE_entry_point, CE_tgt_point, PE_tgt_point,
                                             CE_SL_point, PE_SL_point, dateary)
            final_pnl = self.calcFinalPnl(self, trade_flag, CE_entry_pp, PE_entry_pp, CE_tgt_pp, PE_tgt_pp, CE_SL_pp, PE_SL_pp,
                     CE_Strike, PE_Strike, dayCloseP, dayToExp, close_iv)

            if(final_pnl > 0):
                self.strike_rate = self.strike_rate +1
            

        extra_pnl = 0
        if(self.pnl_strategy == 2):
           
            if(final_pnl > 0):
                extra_pnl = self.calcExtraPnl(self, trade_flag, CE_entry_pp, PE_entry_pp, CE_tgt_pp, PE_tgt_pp, CE_SL_pp, PE_SL_pp,
                     CE_Strike, PE_Strike, dayCloseP, dayToExp, close_iv, CE_tgt_point, PE_tgt_point)
                

        self.writeTradeLog(self, cur_date, [cur_date, trade_flag, final_pnl, extra_pnl])
        print(cur_date, trade_flag, final_pnl, extra_pnl)
            
        return final_pnl + extra_pnl
        '''
        self.index_data_ary[idx].append(self.iv_data_ary[idx][1])
        '''
    def calcExtraPnl(self, trade_flag, CE_entry_pp, PE_entry_pp, CE_tgt_pp, PE_tgt_pp, CE_SL_pp, PE_SL_pp,
                     CE_Strike, PE_Strike, dayCloseP, dayToExp, close_iv, CE_tgt_point, PE_tgt_point):
        extra_pnl = 0
        #here the dayCloseP should be high or low of the day to get better idea
        
        if(trade_flag == 'PE_pos_pnl' and dayCloseP < (PE_tgt_point - self.extra_retr)):
            PE_close_pp = self.opInst.calcPrem(self.opInst, dayCloseP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            extra_pnl = PE_close_pp - PE_entry_pp
        elif(trade_flag == 'CE_pos_pnl' and dayCloseP > (CE_tgt_point + self.extra_retr)):
            CE_close_pp = self.opInst.calcPrem(self.opInst, dayCloseP, CE_Strike, dayToExp-0.9, close_iv-1, 'CE')
            extra_pnl = CE_close_pp - CE_entry_pp

        return math.floor(extra_pnl)    
            
        
    def calcFinalPnl(self, trade_flag, CE_entry_pp, PE_entry_pp, CE_tgt_pp, PE_tgt_pp, CE_SL_pp, PE_SL_pp,
                     CE_Strike, PE_Strike, dayCloseP, dayToExp, close_iv):
        '''
        calculate Pnl for each trade_flag type for positive and negative pnl.
        check if trade_flag = CE_trade
            take final closeP and calc CE_close_exit_pp
        check if trade_flag = PE_trade
            take final closeP and calc PE_close_exit_pp
        calculate pnl accordingly
            
        calc final Pnl
        '''
        final_pnl = 0
        if(trade_flag == 'PE_pos_pnl'):
            final_pnl = PE_tgt_pp - PE_entry_pp
        elif(trade_flag == 'PE_neg_pnl'):
            final_pnl = PE_SL_pp - PE_entry_pp
        elif(trade_flag == 'CE_pos_pnl'):
            final_pnl = CE_tgt_pp - CE_entry_pp
        elif(trade_flag == 'CE_neg_pnl'):
            final_pnl = CE_SL_pp - CE_entry_pp
        elif(trade_flag == 'PE_trade'):
            PE_close_pp = self.opInst.calcPrem(self.opInst, dayCloseP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            final_pnl = PE_close_pp - PE_entry_pp
        elif(trade_flag == 'CE_trade'):
            CE_close_pp = self.opInst.calcPrem(self.opInst, dayCloseP, CE_Strike, dayToExp-0.9, close_iv-1, 'CE')
            final_pnl = CE_close_pp - CE_entry_pp

        return math.floor(final_pnl)
        
    def checkEntryTime(self, cur_dt_time_str):
        cur_date_format = "%Y-%m-%dT%H:%M:%S%z"
        cur_dt_time = datetime.datetime.strptime(cur_dt_time_str, cur_date_format)
        cur_hr = cur_dt_time.hour
        cur_min = cur_dt_time.minute
        return (cur_hr <= 14 and cur_min <= 35)
            
        
    #1
    def retrAlgoStrategy(self, cur_date, cur_dt_object, CE_entry_point, PE_entry_point, CE_tgt_point, PE_tgt_point,
                         CE_SL_point, PE_SL_point, 
                         dateary):
       
        #print(cur_dt_object)
        CE_exit = 0
        PE_exit = 0
        highP = 0
        lowP = 0
        trade_flag = ''

        '''
        loop thru dateary (skip 1st candle)
        from next OHLC data,
        check if trade_flag is blank
            and check if highP has reached PE_entry_point
            if true, mark trade_flag = PE_trade

        check if trade_flag is blank
            and check if lowP has reached CE_entry_point
            if true, mark trade_flag = CE_trade

        if trade_flag = CE_trade
            check if high_P has reached CE_tgt_point
            if true, mark trade_flag = CE_pos_pnl
            Or
            check if low_p has reached CE_SL_point
            if true, mark trade_flag = CE_neg_pnl
        
        if trade_flag = PE_trade
            check if low_P has reached PE_tgt_point
            if true, mark trade_flag = PE_pos_pnl
            Or
            check if high_p has reached PE_SL_point
            if true, mark trade_flag = PE_neg_pnl

        return trade_Flag
        
        '''
        datalen = len(dateary)
        CE_entry_time = ''
        PE_entry_time = ''
        CE_exit_time = ''
        PE_exit_time = ''
        i = 1
        while i < datalen:
            highP = math.floor(float(dateary[i][2]))
            lowP = math.floor(float(dateary[i][3]))
            closeP = math.floor(float(dateary[i][4]))
            cur_dt_time_str = dateary[i][0]
            validEntryTime = self.checkEntryTime(self, cur_dt_time_str)
            if(trade_flag == '' and highP > PE_entry_point and validEntryTime):
                trade_flag = 'PE_trade'
                PE_entry_time = cur_dt_time_str
                
            elif(trade_flag == 'PE_trade' and lowP < PE_tgt_point):               
                PE_exit_time = cur_dt_time_str
                trade_flag = 'PE_pos_pnl'                
                break
            elif(trade_flag == 'PE_trade' and highP > PE_SL_point):               
                PE_exit_time = cur_dt_time_str
                trade_flag = 'PE_neg_pnl'                
                break

            if(trade_flag == '' and lowP < CE_entry_point):
                trade_flag = 'CE_trade'
                CE_entry_time = cur_dt_time_str
                
            elif(trade_flag == 'CE_trade' and highP > CE_tgt_point):               
                CE_exit_time = cur_dt_time_str
                trade_flag =  'CE_pos_pnl'                
                break
            elif(trade_flag == 'CE_trade' and lowP < CE_SL_point):               
                CE_exit_time = cur_dt_time_str
                trade_flag = 'CE_neg_pnl'                
                break           
            
            i = i +1

        if(trade_flag[0:2] == 'CE'):
            self.writeTradeLog(self, cur_date, [trade_flag, ':entry:', CE_entry_time, CE_entry_point, ':exit:', CE_exit_time,
                                                CE_tgt_point, 'SL:', CE_SL_point])
        elif(trade_flag[0:2] == 'PE'):
            self.writeTradeLog(self, cur_date, [trade_flag, ':entry:', PE_entry_time, PE_entry_point, ':exit:', PE_exit_time,
                                                PE_tgt_point, 'SL:', PE_SL_point])
        return trade_flag
    
    def dayToExpiry(self, day):
        #currenty ommitting holiday logic
        dayToExp = 1
        if(day == 0):
            dayToExp = 4
        elif(day == 1):
            dayToExp = 3
        elif(day == 2):
            dayToExp = 2
        elif(day == 3):
            dayToExp = 0.95    
        elif(day == 4):
            dayToExp = 7
            
        return dayToExp
            
def main():
    nsTest = NiftyIntradayFiveMinOHLCAlgoTest
    nsTest.opInst = optionPCalc.OptionsPriceCalculator
    nsTest.retracement = 50
    nsTest.extra_retr = 50
    nsTest.threshold = 90
    nsTest.SL_threshold = 30
    nsTest.pnl_strategy = 2
    nsTest.debug_flag = 1
    nsTest.strikes_choose_logic = 1
    nsTest.slippage_txn_cost = 1
    nsTest.readOHLCDataFile(nsTest, 'C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\data\\hist\\Nifty_5min_fromJan2022.txt');
    nsTest.readIVDataFile(nsTest, 'C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\data\\hist\\hist_india_vix_08-Feb-2019_27-May-2022.csv')
    nsTest.backTestStrategy(nsTest)
    print('Entry threshold from 1st 5min_c H/L :[', nsTest.threshold, '], SL :[', nsTest.SL_threshold,
          '], 1st Tgt retr: [', nsTest.retracement, '], 2nd Tgt/DayClose Tgt for 2nd lot: [', nsTest.extra_retr,
          '], Pnl strategy: lots:',nsTest.pnl_strategy)
    '''
    CE_entry = nsTest.opInst.calcPrem(nsTest.opInst, 16290, 16250, 4, 22.1, 'CE')
    PE_entry = nsTest.opInst.calcPrem(nsTest.opInst, 16290, 16300, 4, 23.1, 'PE')
    print(CE_entry, PE_entry)    
    '''
if __name__=="__main__":
    msg = main()    
