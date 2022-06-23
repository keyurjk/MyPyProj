import csv, math, statistics, datetime, json, datetime, re
import sys
sys.path.append(r"C:\Users\keyur\Documents\Keyur\TradeBook\PythonPrograms")

import OptionsPriceCalculator as optionPCalc
#import os, urllib.request, concurrent.futures  
'''
version1: Nifty index straddle backtest. (10-June-2022)
Program pseudocode.
Read daily OHLC of Nifty (Daily candle)
Attach IV data. PE IV same, CE IV (-2) for ATM options.
(IV used from India VIX index data)
Calculate Open PP nearest Straddle. 
Calculate CE and PE strikes.
Take equi distance ATM or nearest ITM option.  
E.g Open PP 16264 => 16250 CE and 16300 PE.
Open PP 16105 => 16100 CE and 16100 PE
Open PP 16115 = 16100 CE and 16150 PE

Calculate entry PP , Spot = OpenPP, strike, VIX open of the day.

Calculate Exit PP at 90 points.
Calculate 90 points High from Open if high >= 90 points mark.
Calculate 90 points low from Open if low <= 90 points mark.

1. Long: Calculate PnL for both CE and PE exit together.
2. Long: Calculate PnL for one side at 90 points diff and other at EOD.
3. Short: Calculate PnL for both CE and PE exit together.
4. Short: Calculate PnL for one side at 90 points diff and other at EOD.
5. Long: Calculate PnL for one side at 90 points diff and other at 50 points retracement from there.
6. Short: Calculate PnL for one side at 90 points diff and other at 50 points retracement from there.

'''
class NiftyStraddleTestWithVix:

    iv_data_ary = []
    index_data_ary = []
    opInst = None
    pnl_strategy = 1
    debug_flag = 0
    slippage_txn_cost = 3
    retracement = 50
    ATR = 185
    strikes_choose_logic = 1
    
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

        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            self.index_data_ary = list(reader)
            del self.index_data_ary[0]
            i = 0
            while i < 2:
                print(self.index_data_ary[i])
                i = i + 1

    def backTestStrategy(self):
        # merge datau
        datalen = len(self.index_data_ary)
        i = 0
        cum_pnl = 0
        strike_rate = 0
        pos_pnl = 0
        neg_pnl = 0
        while i < datalen-5:
            daypnl = self.calculateStrikesAndPremAndPnl(self, i)
            cum_pnl = cum_pnl + daypnl            
            i = i+1
            if(daypnl > 0):
                strike_rate = strike_rate + 1
                pos_pnl = pos_pnl + daypnl
            elif(daypnl < 0):
                neg_pnl = neg_pnl - daypnl
                
        print('strategy', self.pnl_strategy, 'datalen',i, 'cum_pnl', cum_pnl,
              'strike_rate', strike_rate, 'pos_pnl', pos_pnl, 'neg_pnl', neg_pnl, )
    
    def calculateStrikesAndPremAndPnl(self, idx):
        #print(self.index_data_ary)
        cur_date = self.index_data_ary[idx][0]
        iv_date = self.iv_data_ary[idx][0]
        cur_date_format = "%d/%m/%Y"
        iv_date_format = "%d-%b-%Y"
        cur_dt_object = datetime.datetime.strptime(cur_date, cur_date_format)
        iv_dt_object = datetime.datetime.strptime(iv_date, iv_date_format)
        if (cur_dt_object != iv_dt_object):
            print(cur_date, 'Date not matching', iv_date)
            return 0
        day = cur_dt_object.weekday()
        dayToExp = self.dayToExpiry(self, day, idx)
        cur_iv = float(self.iv_data_ary[idx][1])
        close_iv = float(self.iv_data_ary[idx][4])
        openP = math.floor(float(self.index_data_ary[idx][1])) 
        highP = math.floor(float(self.index_data_ary[idx][2]))
        lowP = math.floor(float(self.index_data_ary[idx][3]))
        closeP = math.floor(float(self.index_data_ary[idx][4]))

        if(cur_iv > 32):
            print('Skipping the day for high IV ', cur_iv, ' day ', cur_date)
            return 0
        
        PE_Strike = 0
        CE_Strike = 0
        base = round(openP, -2)        
        #equi distance strike logic
        if(self.strikes_choose_logic == 1):
            if(base - openP >= 10):
                PE_Strike = base
                CE_Strike = PE_Strike - 50
            elif(base - openP <= -10):
                CE_Strike = base
                PE_Strike = CE_Strike + 50
            elif(abs(base - openP) <= 10):
                CE_Strike = base
                PE_Strike = CE_Strike
        elif(self.strikes_choose_logic == 2):
            # same strike logic
            PE_Strike = base
            CE_Strike = base
            #print('::same strike logic::')
        elif(self.strikes_choose_logic == 3):        
            #100 points ITM strikes logic
            PE_Strike = base +100
            CE_Strike = base -100
        elif(self.strikes_choose_logic == 4):
            #ATR point OTM strikes logic            
            PE_Strike = round(openP-self.ATR, -2)
            CE_Strike = round(openP+self.ATR, -2)
            
        #print(cur_date, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp)
        CE_entry = self.opInst.calcPrem(self.opInst, openP, CE_Strike, dayToExp, cur_iv-1, 'CE')
        PE_entry = self.opInst.calcPrem(self.opInst, openP, PE_Strike, dayToExp, cur_iv, 'PE')
        #print(cur_date, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)

        #exit Spot (90 +/-)
        threshold = 90
        if (cur_dt_object.year == 2019):
            threshold = 70
        elif (cur_dt_object.year == 2020):
            threshold = 80
        elif (cur_dt_object.year == 2021):
            threshold = 85    
        high_exit = openP + threshold
        low_exit = openP - threshold
        
        final_pnl = 0
        if(self.pnl_strategy == 1):
            final_pnl = self.longThresholdReachExitBothStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv)
        elif(self.pnl_strategy == 2):
            final_pnl = self.longThresholdReachExitOtherAtCloseStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv)
        elif(self.pnl_strategy == 3):
            final_pnl = self.shortThresholdReachExitBothStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv)
        elif(self.pnl_strategy == 4):
            final_pnl = self.shortThresholdReachExitOtherAtCloseStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv)
        elif(self.pnl_strategy == 5):
            final_pnl = self.longThresholdReachExitOtherAtRetracementStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv)
        elif(self.pnl_strategy == 6):
            final_pnl = self.shortThresholdReachExitOtherAtRetracementStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv)

        return final_pnl - self.slippage_txn_cost
        '''
        self.index_data_ary[idx].append(self.iv_data_ary[idx][1])
        '''
    #1
    def longThresholdReachExitBothStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv):
        CE_exit = 0
        PE_exit = 0
        
        exit_flag = ''
        if(highP > high_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, high_exit, CE_Strike, dayToExp, cur_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, high_exit, PE_Strike, dayToExp, cur_iv, 'PE')
            exit_flag = 'high_exit'
        elif(CE_exit == 0 and lowP < low_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, low_exit, CE_Strike, dayToExp, cur_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, low_exit, PE_Strike, dayToExp, cur_iv, 'PE')
            exit_flag = 'low_exit'
        elif(CE_exit == 0 and PE_exit == 0):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            exit_flag = 'close_exit'

        
        final_pnl = math.floor((CE_exit + PE_exit) - (CE_entry + PE_entry))
        if(self.debug_flag == 1 and cur_dt_object.year == 2021 and cur_dt_object.month == 3):
            print(cur_dt_object, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)
            print(cur_dt_object, exit_flag, '::highP', highP, 'lowP', lowP, 'closeP', closeP, 'CE_exit', CE_exit, 'PE_exit', PE_exit, 'final_pnl: ', final_pnl)
        return final_pnl
    #2
    def longThresholdReachExitOtherAtCloseStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv):
        CE_exit = 0
        PE_exit = 0
        
        exit_flag = ''
        if(highP > high_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, high_exit, CE_Strike, dayToExp, cur_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            exit_flag = 'high_exit'
        elif(CE_exit == 0 and lowP < low_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, low_exit, PE_Strike, dayToExp, cur_iv, 'PE')
            exit_flag = 'low_exit'
        elif(CE_exit == 0 and PE_exit == 0):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            exit_flag = 'close_exit'

        
        final_pnl = math.floor((CE_exit + PE_exit) - (CE_entry + PE_entry))
        if(self.debug_flag == 1 and cur_dt_object.year == 2023 and cur_dt_object.month == 3):
            print(cur_dt_object, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)
            print(cur_dt_object, exit_flag, '::highP', highP, 'lowP', lowP, 'closeP', closeP, 'CE_exit', CE_exit, 'PE_exit', PE_exit, 'final_pnl: ', final_pnl)
        return final_pnl
    #5
    def longThresholdReachExitOtherAtRetracementStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv):
        CE_exit = 0
        PE_exit = 0
        
        exit_flag = ''
        if(highP > high_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, high_exit, CE_Strike, dayToExp-0.1, cur_iv-1, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, high_exit-self.retracement, PE_Strike, dayToExp-0.2, cur_iv-1, 'PE')
            exit_flag = 'high_exit'
        elif(CE_exit == 0 and lowP < low_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, low_exit+self.retracement, CE_Strike, dayToExp-0.2, cur_iv-1, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, low_exit, PE_Strike, dayToExp-0.1, cur_iv-1, 'PE')
            exit_flag = 'low_exit'
        elif(CE_exit == 0 and PE_exit == 0):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            exit_flag = 'close_exit'

        
        final_pnl = math.floor((CE_exit + PE_exit) - (CE_entry + PE_entry))
        if(self.debug_flag == 1 and cur_dt_object.year == 2021 and cur_dt_object.month == 3):
            print(cur_dt_object, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)
            print(cur_dt_object, exit_flag, '::highP', highP, 'lowP', lowP, 'closeP', closeP, 'CE_exit', CE_exit, 'PE_exit', PE_exit, 'final_pnl: ', final_pnl)
        return final_pnl
    #3
    def shortThresholdReachExitBothStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv):
        CE_exit = 0
        PE_exit = 0
        CE_entry = 0 - CE_entry
        PE_entry = 0 - PE_entry
        exit_flag = ''
        if(highP > high_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, high_exit, CE_Strike, dayToExp, cur_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, high_exit, PE_Strike, dayToExp, cur_iv, 'PE')
            exit_flag = 'high_exit'
        elif(CE_exit == 0 and lowP < low_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, low_exit, CE_Strike, dayToExp, cur_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, low_exit, PE_Strike, dayToExp, cur_iv, 'PE')
            exit_flag = 'low_exit'
        elif(CE_exit == 0 and PE_exit == 0):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            exit_flag = 'close_exit'

        
        final_pnl = math.floor(abs((CE_entry + PE_entry)) - (CE_exit + PE_exit))
        if(self.debug_flag == 1 and cur_dt_object.year == 2023 and cur_dt_object.month == 3):
            print(cur_dt_object, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)
            print(cur_dt_object, exit_flag, '::highP', highP, 'lowP', lowP, 'closeP', closeP, 'CE_exit', CE_exit, 'PE_exit', PE_exit, 'final_pnl: ', final_pnl)
        return final_pnl

    #4
    def shortThresholdReachExitOtherAtCloseStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv):
        CE_exit = 0
        PE_exit = 0
        CE_entry = 0 - CE_entry
        PE_entry = 0 - PE_entry
        exit_flag = ''
        if(highP > high_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, high_exit, PE_Strike, dayToExp, cur_iv, 'PE')
            exit_flag = 'high_exit'
        elif(CE_exit == 0 and lowP < low_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, low_exit, CE_Strike, dayToExp, cur_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            exit_flag = 'low_exit'
        elif(CE_exit == 0 and PE_exit == 0):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            exit_flag = 'close_exit'

        
        final_pnl = math.floor(abs((CE_entry + PE_entry)) - (CE_exit + PE_exit))
        if(self.debug_flag == 1 and cur_dt_object.year == 2020 and cur_dt_object.month == 3):
            print(cur_dt_object, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)
            print(cur_dt_object, exit_flag, '::highP', highP, 'lowP', lowP, 'closeP', closeP, 'CE_exit', CE_exit, 'PE_exit', PE_exit, 'final_pnl: ', final_pnl)
        return final_pnl
    #6
    def shortThresholdReachExitOtherAtRetracementStrategy(self, cur_dt_object, openP, highP, high_exit, lowP, low_exit, closeP,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv):
        CE_exit = 0
        PE_exit = 0
        CE_entry = 0 - CE_entry
        PE_entry = 0 - PE_entry
        exit_flag = ''
        if(highP > high_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, high_exit-self.retracement, CE_Strike, dayToExp, cur_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, high_exit, PE_Strike, dayToExp, cur_iv, 'PE')
            exit_flag = 'high_exit'
        elif(CE_exit == 0 and lowP < low_exit):
            CE_exit = self.opInst.calcPrem(self.opInst, low_exit, CE_Strike, dayToExp, cur_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, low_exit-self.retracement, PE_Strike, dayToExp, cur_iv, 'PE')
            exit_flag = 'low_exit'
        elif(CE_exit == 0 and PE_exit == 0):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            exit_flag = 'close_exit'

        
        final_pnl = math.floor(abs((CE_entry + PE_entry)) - (CE_exit + PE_exit))
        if(self.debug_flag == 1 and cur_dt_object.year == 2020 and cur_dt_object.month == 3):
            print(cur_dt_object, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)
            print(cur_dt_object, exit_flag, '::highP', highP, 'lowP', lowP, 'closeP', closeP, 'CE_exit', CE_exit, 'PE_exit', PE_exit, 'final_pnl: ', final_pnl)
        return final_pnl

    
    def dayToExpiry(self, day, idx):
        #print('dayToExp TODO')
        dayToExp = 1
        forward_idx = 0
        if(day == 0):
            dayToExp = 4
            forward_idx = 3
        elif(day == 1):
            dayToExp = 3
            forward_idx = 2
        elif(day == 2):
            dayToExp = 2
            forward_idx = 1        
        elif(day == 4):
            dayToExp = 7
            forward_idx = 4
            
        exp_date = self.index_data_ary[idx + forward_idx][0]
        exp_date_format = "%d/%m/%Y"
        exp_dt_object = datetime.datetime.strptime(exp_date, exp_date_format)
        if(exp_dt_object.weekday() == 4):       #next data friday, so take wednesday
            dayToExp = dayToExp - 1
        #if(exp_dt_object.weekday() == 2):       #next data missing skipping
        #    dayToExp = max(dayToExp - 2,1)
        return dayToExp
            
def main():
    nsTest = NiftyStraddleTestWithVix
    nsTest.opInst = optionPCalc.OptionsPriceCalculator
    nsTest.ATR = 185
    nsTest.strikes_choose_logic = 4
    nsTest.pnl_strategy = 4
    nsTest.debug_flag = 1
    nsTest.slippage_txn_cost = 2
    nsTest.readOHLCDataFile(nsTest, 'C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\NSE_Index_data.csv');
    nsTest.readIVDataFile(nsTest, 'C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\data\\hist\\hist_india_vix_08-Feb-2019_27-May-2022_org.csv')
    nsTest.backTestStrategy(nsTest)
if __name__=="__main__":
    msg = main()    
    
