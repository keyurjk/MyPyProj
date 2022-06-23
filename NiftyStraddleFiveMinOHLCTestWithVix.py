import csv, math, statistics, datetime, json, datetime, re
import sys
sys.path.append(r"C:\Users\keyur\Documents\Keyur\TradeBook\PythonPrograms")

import OptionsPriceCalculator as optionPCalc

'''
Nifty straddle test based on 5min OHLC data.

read 5 min OHLC data for a day.
Collect data for a day and
Attach OpenIV data from VIX file. PE IV same, CE IV (-2) for ATM options.
(IV used from India VIX index data)
Calculate Open PP nearest Straddle. 
Calculate CE and PE strikes.
Take equi distance ATM or nearest ITM option.  
E.g Open PP 16264 => 16250 CE and 16300 PE.
Open PP 16105 => 16100 CE and 16100 PE
Open PP 16115 = 16100 CE and 16150 PE

Calculate entry PP , Spot = OpenPP, strike, based on VIX open of the day.

use threashold logic for winning side exit. calculate and store Pnl.
Note down time.
Go further in day and use x point retracement mark touch down. If touches
calculate losing side exit PP and Pnl.

calculate final Pnl for the day.

'''

class NiftyStraddleFiveMinOHLCTestWithVix:

    iv_data_ary = []
    #this is an map with key as date
    #and value 2D array, 1st element array of 5min OHLC for the day, 2nd elem is IV.
    daily_data_dict = dict()
    index_data_ary = []
    all_data = []
    opInst = None
    pnl_strategy = 1
    debug_flag = 0
    slippage_txn_cost = 3
    retracement = 90
    threshold = 90
    #1. ATM equi distance strikes, 2. ATM Same strikes (so one will be ITM), 3. 100 points ITM strikes 
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
            cum_pnl = cum_pnl + self.calculateStrikesAndPremAndPnl(self, datekey, dateary, idx)
            idx = idx + 1
        print('datalen',idx, 'cum_pnl', cum_pnl, 'strategy', self.pnl_strategy, 'strikes_choose_logic', self.strikes_choose_logic)
    
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

        openP = math.floor(float(dateary[0][1])) 
        high_exit = openP + self.threshold
        low_exit = openP - self.threshold
        high_retr = low_exit + self.retracement
        low_retr = high_exit - self.retracement
                
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
        
        #print(cur_date, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp)
        CE_entry = self.opInst.calcPrem(self.opInst, openP, CE_Strike, dayToExp, cur_iv-1, 'CE')
        PE_entry = self.opInst.calcPrem(self.opInst, openP, PE_Strike, dayToExp, cur_iv, 'PE')
        #print(cur_date, 'openP', openP, 'CE', CE_Strike, 'PE', PE_Strike, 'IV', cur_iv, 'day', day, dayToExp, CE_entry, PE_entry)

        
        final_pnl = 0
        if(self.pnl_strategy == 5):
            final_pnl = self.longThresholdReachExitOtherAtRetracementStrategy(self, cur_dt_object, openP, high_exit, low_exit,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv, high_retr, low_retr, dateary)
        elif(self.pnl_strategy == 6):
            final_pnl = self.shortThresholdReachExitOtherAtRetracementStrategy(self, cur_dt_object, openP, high_exit, low_exit,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv, high_retr, low_retr, dateary)
        

        return final_pnl - self.slippage_txn_cost
        '''
        self.index_data_ary[idx].append(self.iv_data_ary[idx][1])
        '''
    #5
    def longThresholdReachExitOtherAtRetracementStrategy(self, cur_dt_object, openP, high_exit, low_exit,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv,
                                                         high_retr, low_retr, dateary):
        CE_exit = 0
        PE_exit = 0
        highP = 0
        lowP = 0
        closeP = 0
        exit_flag = ''

        '''
        loop thru dateary, take each OHLC
        check if highP has reached high_Exit tgt
        if true, calc CE_exit PP and mark high_exit and loop thru next data for low_retr exit.
        If touches low_retr point than calc PE_exit at low_retr
        if not then calc PE_exit at closeP.
        calc final Pnl

        
        '''
        datalen = len(dateary)
        CE_exit_time = ''
        PE_exit_time = ''
        CE_exit_point = 0
        PE_exit_point = 0
        i = 0
        while i < datalen:
            highP = math.floor(float(dateary[i][2]))
            lowP = math.floor(float(dateary[i][3]))
            closeP = math.floor(float(dateary[i][4]))
            if(exit_flag == '' and highP > high_exit):
                CE_exit = self.opInst.calcPrem(self.opInst, high_exit, CE_Strike, dayToExp-0.1, cur_iv-1, 'CE')                
                exit_flag = 'high_exit'
                CE_exit_time = dateary[i][0]
                CE_exit_point = high_exit
            elif(exit_flag == 'high_exit' and lowP < low_retr):
                PE_exit = self.opInst.calcPrem(self.opInst, low_retr, PE_Strike, dayToExp-0.2, cur_iv-1, 'PE')
                PE_exit_time = dateary[i][0]
                exit_flag = exit_flag + ':low_retr:'
                PE_exit_point = low_retr
                break

            if(exit_flag == '' and lowP < low_exit):
                PE_exit = self.opInst.calcPrem(self.opInst, low_exit, PE_Strike, dayToExp-0.1, cur_iv-1, 'PE')
                exit_flag = 'low_exit'
                PE_exit_time = dateary[i][0]
                PE_exit_point = low_exit
            elif(exit_flag == 'low_exit' and highP > high_retr):
                CE_exit = self.opInst.calcPrem(self.opInst, high_retr, CE_Strike, dayToExp-0.2, cur_iv-1, 'CE')
                CE_exit_time = dateary[i][0]
                exit_flag = exit_flag + ':high_retr:'
                CE_exit_point = high_retr
                break
            i = i +1

        if(exit_flag == ''):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            CE_exit_time = dateary[i-1][0]
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            PE_exit_time = dateary[i-1][0]
            exit_flag = 'close_exit'
        elif(exit_flag == 'low_exit' and CE_exit == 0):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            CE_exit_time = dateary[i-1][0]
            exit_flag = exit_flag + ':CE_Close_exit'
        elif(exit_flag == 'high_exit' and PE_exit == 0):
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            PE_exit_time = dateary[i-1][0]
            exit_flag = exit_flag + ':PE_Close_exit'
            
        
        final_pnl = math.floor((CE_exit + PE_exit) - (CE_entry + PE_entry))
        if(self.debug_flag == 1 or final_pnl < -50):
            print('inputs::', 'openP', openP, 'closeP', closeP, 'CE', CE_Strike, 'PE', PE_Strike,
                  'IV', cur_iv, 'day', day, 'dayToExp:', dayToExp, 'CE_entry', CE_entry, 'PE_entry', PE_entry) 
            print('CE_exititme', CE_exit_time, 'CE_exit_point', CE_exit_point, 'CE_exit_price', CE_exit, '::exit_flag::', exit_flag) 
            print('PE_exititme', PE_exit_time, 'PE_exit_point', PE_exit_point, 'PE_exit_price', PE_exit, '::::::::::::::::::::final_pnl::::::::::::: ', final_pnl)
        return final_pnl
    #6
    def shortThresholdReachExitOtherAtRetracementStrategy(self, cur_dt_object, openP, high_exit, low_exit,
                                           CE_Strike, PE_Strike, CE_entry, PE_entry, day, dayToExp, cur_iv, close_iv,
                                                         high_retr, low_retr, dateary):

        CE_entry = 0 - CE_entry
        PE_entry = 0 - PE_entry
        CE_exit = 0
        PE_exit = 0
        highP = 0
        lowP = 0
        closeP = 0
        exit_flag = ''

        '''
        loop thru dateary, take each OHLC
        check if highP has reached high_Exit tgt
        if true, calc CE_exit PP and mark high_exit and loop thru next data for low_retr exit.
        If touches low_retr point than calc PE_exit at low_retr
        if not then calc PE_exit at closeP.
        calc final Pnl

        
        '''
        datalen = len(dateary)
        CE_exit_time = ''
        PE_exit_time = ''
        CE_exit_point = 0
        PE_exit_point = 0
        i = 0
        while i < datalen:
            highP = math.floor(float(dateary[i][2]))
            lowP = math.floor(float(dateary[i][3]))
            closeP = math.floor(float(dateary[i][4]))
            if(exit_flag == '' and highP > high_exit):
                PE_exit = self.opInst.calcPrem(self.opInst, high_exit, PE_Strike, dayToExp-0.2, cur_iv-1, 'PE')
                exit_flag = 'high_exit'
                PE_exit_time = dateary[i][0]
                PE_exit_point = high_exit
            elif(exit_flag == 'high_exit' and lowP < low_retr):
                CE_exit = self.opInst.calcPrem(self.opInst, low_retr, CE_Strike, dayToExp-0.2, cur_iv-1, 'CE')
                CE_exit_time = dateary[i][0]
                exit_flag = exit_flag + ':low_retr:'
                CE_exit_point = low_retr
                break
            
            if(exit_flag == '' and lowP < low_exit):
                CE_exit = self.opInst.calcPrem(self.opInst, low_exit, CE_Strike, dayToExp-0.2, cur_iv-1, 'CE')
                CE_exit_time = dateary[i][0]
                exit_flag = 'low_exit'
                CE_exit_time = dateary[i][0]
                CE_exit_point = low_exit
            elif(exit_flag == 'low_exit' and highP > high_retr):
                PE_exit = self.opInst.calcPrem(self.opInst, high_retr, PE_Strike, dayToExp-0.2, cur_iv-1, 'PE')
                PE_exit_time = dateary[i][0]
                exit_flag = exit_flag + ':high_retr:'
                PE_exit_point = high_retr
                break
            i = i +1

        if(exit_flag == ''):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            CE_exit_time = dateary[i-1][0]
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            PE_exit_time = dateary[i-1][0]
            exit_flag = 'close_exit'
            PE_exit_point = closeP
            CE_exit_point = closeP
        elif(exit_flag == 'high_exit' and CE_exit == 0):
            CE_exit = self.opInst.calcPrem(self.opInst, closeP, CE_Strike, dayToExp-0.9, close_iv, 'CE')
            CE_exit_time = dateary[i-1][0]
            exit_flag = exit_flag + ':CE_Close_exit'
            CE_exit_point = closeP
        elif(exit_flag == 'low_exit' and PE_exit == 0):            
            PE_exit = self.opInst.calcPrem(self.opInst, closeP, PE_Strike, dayToExp-0.9, close_iv, 'PE')
            PE_exit_time = dateary[i-1][0]
            exit_flag = exit_flag + ':PE_Close_exit'
            PE_exit_point = closeP 
        
        final_pnl = math.floor(abs((CE_entry + PE_entry)) - (CE_exit + PE_exit))
        if(self.debug_flag == 1 or final_pnl > 50):
            print('inputs::', 'openP', openP, 'closeP', closeP, 'CE', CE_Strike, 'PE', PE_Strike,
                  'IV', cur_iv, 'day', day, 'dayToExp:', dayToExp, 'CE_entry', CE_entry, 'PE_entry', PE_entry) 
            print('CE_exititme', CE_exit_time, 'CE_exit_point', CE_exit_point, 'CE_exit_price', CE_exit, '::exit_flag::', exit_flag) 
            print('PE_exititme', PE_exit_time, 'PE_exit_point', PE_exit_point, 'PE_exit_price', PE_exit, '::::::::::::::::::::::final_pnl::::::::::: ', final_pnl)
        return final_pnl

    
    def dayToExpiry(self, day):
        #currenty ommitting holiday logic
        dayToExp = 1
        if(day == 0):
            dayToExp = 4
        elif(day == 1):
            dayToExp = 3
        elif(day == 2):
            dayToExp = 2
        elif(day == 4):
            dayToExp = 7
            
        return dayToExp
            
def main():
    nsTest = NiftyStraddleFiveMinOHLCTestWithVix
    nsTest.opInst = optionPCalc.OptionsPriceCalculator
    nsTest.retracement = 90
    nsTest.threshold = 120
    nsTest.pnl_strategy = 5
    nsTest.debug_flag = 0
    nsTest.strikes_choose_logic = 1
    nsTest.slippage_txn_cost = 2
    nsTest.readOHLCDataFile(nsTest, 'C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\data\\hist\\Nifty_5min_fromJan2022.txt');
    nsTest.readIVDataFile(nsTest, 'C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\data\\hist\\hist_india_vix_08-Feb-2019_27-May-2022.csv')
    nsTest.backTestStrategy(nsTest)
    '''
    CE_entry = nsTest.opInst.calcPrem(nsTest.opInst, 16290, 16250, 4, 22.1, 'CE')
    PE_entry = nsTest.opInst.calcPrem(nsTest.opInst, 16290, 16300, 4, 23.1, 'PE')
    print(CE_entry, PE_entry)    
    '''
if __name__=="__main__":
    msg = main()    
