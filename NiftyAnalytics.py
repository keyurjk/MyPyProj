import csv, math, statistics, datetime, random
#import os, urllib.request, concurrent.futures  
'''
version1: read bhavcopy files of last 4 days and today live stock data file and mearge in a list and print.
version2: Modified completely for Nifty analytics for daily option PP calculation and entry at open
and exit at high/low/close PP.

'''


    
'''
----------------
'''
class NiftyAnalytics:

    def_ret = 0.1
    oppDif_sl_divisr = 3
    frmt_str = '%d/%m/%Y'
    ITM_OTM = 'ITM'
    #thursday
    day_to_check = 3
    print_flag = 0
    do_analysis_only = 0
    backtest_trading_strategy = 1
    fixed_cost = 5
    simple_exec_flag = 1
    lots_play = 1
    stk_pp_dif = 50
    stage_cnt = 2

    min_points_diff = 2
    max_pnl_perc = 1.5
    min_sl_divisr = 3
    long_max_exit_stddev = 45
    short_max_exit_stddev = 65
    high_volt_ret = 2
    low_volt_ret = 1
    default_volt = 10

    int_rate = 0.1
    default_theta = 0.9
    year_d = 365

    def readOHLCDataFile(self, fileName):

        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            print('=====start=======')
            print('CE TGT:', self.long_max_exit_stddev, 'PE tgt:', self.short_max_exit_stddev)
            print('Strategy: Entry at open, exit both side when one tgt hit Or at EOD both, Volt: 17')
               
            lt = list(reader)
            del lt[0]
            self.tradeReport(self, lt)    
            
        
      
    
    def tradeReport(self, lt):
        print('==========trade report start=======')
        self.execOptionIntraday(self, lt, 1)
               

    def execOptionIntraday(self, lt, local_print_flag):
        self.lots_play = 1
        tc = len(lt)
        long_pos_ret = []
        short_pos_ret = []
        long_neg_ret = []
        short_neg_ret = []
        all_ret = []
        lpr_cnt = 0
        spr_cnt = 0
        exec_cnt = 0
        stage = self.stage_cnt
        prev_yr = 2011
        yearly_ret = 0
        prev_day_ret = 1
        for row in lt:
            #print(row)
            dt_str = row[0]
            dt_fld = datetime.datetime.strptime(dt_str, self.frmt_str)
            cur_yr = dt_fld.year
            weekd = dt_fld.weekday()
            daytoExp = self.calcDaysToExp(self, weekd)
            
            openP = round(float(row[1]),0)
            highP = round(float(row[2]),0)
            lowP = round(float(row[3]),0)
            closeP = round(float(row[4]),0)

            stk = round(openP,-2)            
            
            #taking YD ATR %
            YD_ret = prev_day_ret

                        
            tot_pnl = self.calcPnl(self, long_pos_ret, long_neg_ret, short_pos_ret, short_neg_ret,
                    openP, highP, lowP, closeP, YD_ret, stk, daytoExp)

            #calc today atr
            
            prev_day_ret = round((((closeP - openP)/openP)*100),2)
            
            #all_ret.append([dt_str, l_ret, s_ret, (l_ret+s_ret)])
            all_ret.append([dt_str, tot_pnl])
            lpr_cnt = len(long_pos_ret)
            spr_cnt = len(short_pos_ret)
            yearly_ret = yearly_ret + tot_pnl
            if(cur_yr > prev_yr):
                print(cur_yr, ':- yearly ret----: ', round(yearly_ret,2))
                #print(all_ret)
                stage = stage + 1
                #self.lots_play = self.lots_play + 2
                prev_yr = cur_yr
                all_ret = []
                yearly_ret = 0
        #for loop end
                
        self.generateReport(self, long_pos_ret, long_neg_ret, short_pos_ret, short_neg_ret)
        
        
    def generateReport(self, long_pos_ret, long_neg_ret, short_pos_ret, short_neg_ret):
        
        if(self.print_flag == 1):
            print('long_pos_ret:', long_pos_ret)
            print('long_neg_ret:', long_neg_ret)
            print('short_pos_ret:', short_pos_ret)
            print('short_neg_ret:', short_neg_ret)
            
        lpr = len(long_pos_ret)
        lnr = len(long_neg_ret)
        spr = len(short_pos_ret)
        snr = len(short_neg_ret)
        print('count(long_pos_ret):', lpr, ' sum(lpr)', round(sum(long_pos_ret),2),
              ' count(long_neg_ret):', lnr, 'sum(lnr)', round(sum(long_neg_ret),2),
              'count(short_pos_ret):', spr, 'sum(spr)', round(sum(short_pos_ret),2),
              'count(short_neg_ret):', snr, 'sum(snr)', round(sum(short_neg_ret),2))
        print(': average long ret :', round(((sum(long_pos_ret)+sum(long_neg_ret))/(lpr+lnr)),2),
              ' :stdev of LPR:', round(statistics.stdev(long_pos_ret),2),
              ': average short ret :', round(((sum(short_pos_ret)+sum(short_neg_ret))/(spr+snr)),2),
              ' :stdev of SPR:', round(statistics.stdev(short_pos_ret),2)
              )
        comb_pos_ret = long_pos_ret + short_pos_ret
        comb_neg_ret = long_neg_ret + short_neg_ret
        print(':Combined Positive ret avg:', round(((sum(comb_pos_ret))/(lpr+spr)),2),
              ' :stdev of comb pos:', round(statistics.stdev(comb_pos_ret),2),
              ' :stdev of overall:', round(statistics.stdev((comb_pos_ret+comb_neg_ret)),2) ,
              ' :Overall Total ret:', round((sum(comb_pos_ret)+sum(comb_neg_ret)),2) 
              )
        print('CE TGT:', self.long_max_exit_stddev, 'PE tgt:', self.short_max_exit_stddev)
        print('Strategy: Entry at open, exit both side when one tgt hit Or at EOD both, Volt: 17')
        
    '''
    Execution varation:
    Entry PP of Nifty at BOD +/- 10 points as random.
    4) Keeps SD/ATR/1% from open as high low target.
    5) Enter both sides ATM option. 
    6) calculate entry PP of options.
    7) calcualte target with 1% from open PP as high/low.
    8) Exit strategy.
    Once one side matched target as High/low PP,  exit that side in profit
    and exit other side as loss as first exit strategy.
    2nd exit strategy, exit at EOD close PP +/- 10 points.
    3rd exit strategy, avg out losing side with 1 more lot at the other side exit.
    and then exit that side at EOD close PP +/10 points.

    put all PnL in dift arrays to be analysed.
    '''
   
    
    def calcPnl(self, long_pos_ret, long_neg_ret, short_pos_ret, short_neg_ret,
                    openP, highP, lowP, closeP, yd_ret, stk, daytoExp):
        #print('calcPnl:0', diff)
        pnlCE = 0
        pnlPE = 0
        voltPE = self.calcPEVolt(self, yd_ret)
        voltCE = self.calcCEVolt(self, voltPE, yd_ret)

        profit_tgt_ce = openP + self.long_max_exit_stddev
        profit_tgt_pe = openP - self.short_max_exit_stddev
        
        oppremCE = self.calcPrem(self, openP, stk, daytoExp, voltCE, 'CE')
        oppremPE = self.calcPrem(self, openP, stk, daytoExp, voltPE, 'PE')
        
        hppremCE = self.calcPrem(self, profit_tgt_ce, stk, daytoExp, voltCE-1, 'CE')
        hppremPE = self.calcPrem(self, profit_tgt_ce, stk, daytoExp, voltPE-1, 'PE')

        lppremCE = self.calcPrem(self, profit_tgt_pe, stk, daytoExp, voltCE+1, 'CE')
        lppremPE = self.calcPrem(self, profit_tgt_pe, stk, daytoExp, voltPE+1, 'PE')

        cppremCE = self.calcPrem(self, closeP, stk, daytoExp-0.8, voltCE-1, 'CE')
        cppremPE = self.calcPrem(self, closeP, stk, daytoExp-0.8, voltPE-1, 'PE')
        
        #simple exec, go for high/low PP diff - min_diff
       
        #CE profit exit with PE loss exit flag
        #1st strategy, try exiting other when one side hits target        
        if(lowP <= profit_tgt_pe):
            pnlPE = lppremPE - oppremPE
            pnlCE = lppremCE - oppremCE     #exiting at loss 1st strategy


        if(pnlPE == 0 and highP >= profit_tgt_ce):
            pnlCE = hppremCE - oppremCE
            pnlPE = hppremPE - oppremPE     #exiting at loss 1st strategy
        
        #no target hit
        if(pnlCE == 0 and pnlPE == 0):            
            pnlCE = cppremCE - oppremCE
            pnlPE = cppremPE - oppremPE
            
        '''
        #  2nd exit strategy for not hitting target
        if(pnlPE == 0):
            pnlPE = cppremPE - oppremPE     #at close exit strategy
                
        if(pnlCE == 0):
            pnlCE = cppremCE - oppremCE     #at close exit strategy
        
        '''
        
        # add to correct array
        if(pnlPE > 0):
            short_pos_ret.append(pnlPE)
        else:
            short_neg_ret.append(pnlPE)
        
        if(pnlCE > 0):
            long_pos_ret.append(pnlCE)
        else:
            long_neg_ret.append(pnlCE)
        
        
        '''
        print('calcPnl: stk', stk, 'pot_ce', profit_tgt_ce, 'pot_pe', profit_tgt_pe, 'd2E', daytoExp,
              'ydr', yd_ret, 'voltPE', voltPE, 'voltCE', voltCE)    
        print('prem:CE', oppremCE,  hppremCE, lppremCE, cppremCE, 'PE:', oppremPE, hppremPE,  lppremPE,  cppremPE)
        print('pnl', round(pnlCE,2), round(pnlPE,2), 'combined:', round((pnlCE + pnlPE),2))
        '''
        return pnlCE + pnlPE


    def calcPEVolt(self, yd_ret):
        volt = 17
            
        return volt
    
    def calcCEVolt(self, pe_volt, yd_ret):
        volt = pe_volt -2
        return volt    
        
    def calcDaysToExp(self, daytoExp):
        days2Exp = 1
        if(daytoExp == 0):
            days2Exp = 4
        elif(daytoExp == 1):
            days2Exp = 3
        elif(daytoExp == 2):
            days2Exp = 2
        elif(daytoExp == 3):
            days2Exp = 1
        elif(daytoExp == 4):
            days2Exp = 7

        return days2Exp    
            
    def calcPrem(self, spot, strike, dayToExp, volt, CE_PE):
        volt = volt/100
        delta_t = 0.1
        if(dayToExp == 1):
            delta_t = self.default_theta/self.year_d
        else:
            delta_t = dayToExp/self.year_d
            
        d1 = (math.log(spot/strike) + (self.int_rate + (math.pow(volt,2))/2) * delta_t) / (volt*math.sqrt(delta_t))
        d1 = round(d1, 10)

        d2 = (math.log(spot/strike) + (self.int_rate - math.pow(volt,2)/2) * delta_t) / (volt*math.sqrt(delta_t))
        d2 = round(d2, 10)
        Nd1 = round(self.cdf(d1), 10)
        Nd2 = round(self.cdf(d2), 10)
        _Nd1 = round(self.cdf(-1 * d1), 10)
        _Nd2 = round(self.cdf(-1 * d2), 10)
        fv_strike = (strike) * math.exp (-1 * self.int_rate * delta_t)
        prem = 0.0
        if(CE_PE == 'CE'):
            call_prem = spot * Nd1 - fv_strike * Nd2
            prem = round(call_prem, 2)
        elif(CE_PE == 'PE'):
            put_prem = fv_strike * _Nd2 - spot * _Nd1
            prem = round(put_prem, 2)

        return prem

    def cdf(x):
        return 0.5 * math.erfc(- (x- 0) / (1 * math.sqrt(2)))

    def pdf(x):
        m_val = 1 * math.sqrt(2 * math.pi)
        e_val = math.exp(-math.pow(x - 0, 2) / (2 * 1))
        return e_val /m_val
