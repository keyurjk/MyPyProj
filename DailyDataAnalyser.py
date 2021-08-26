import csv, math, statistics, datetime

#import os, urllib.request, concurrent.futures  
'''
version1.1: Nifty index dataanalystics added. (23-July-2021)
version1.2: Added Open To High and Low analysis. With open > YC/Pivot.
version1.3: Analyse particular day of week. 
version1.4: Execution varation, 1 lot, 2 lot, 3 lot with 10-50% gain exit, 50% SL, 2nd lot max exit at STD dev, or at close PP.
version1.5: To calculate realtime PP for entry at open PP with IV range as 14 (short) and (10) long for high volt and 11/9 for low volt
based on previous day ATR or Pivot distance increase/decrease.
'''
class DailyDataAnalyser:

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
            print('Default return set:', self.def_ret, ' , opp diff SL:', self.oppDif_sl_divisr, ', weekday to test:', self.day_to_check)
            lt = list(reader)
            del lt[0]
            if(self.do_analysis_only == 1):
                self.dataAnalytics(self, lt)
            if(self.backtest_trading_strategy == 1):
                self.tradeReport(self, lt)    
            
    def dataAnalytics(self, lt):
        '''
        Current analytics of Open to High and Low return, based on daily returns from close to close.
        Pivot analytics of Crossover of pivot levels to be based on daily ATR calc and contraction and expansion of ATR.
        To check : 1. % openToHigh return and pivot level cross of high when gapup open and cross YC/Pivot. 
        '''
        
        fromdt = lt[0][0]
        ltlen = len(lt)-1
        todt = lt[ltlen][0]

        #print(lt[ltlen-10:ltlen])
        
        
        self.calcDailyClosePPReturnRSI(self, lt, 0)
        #self.calcDailyATRret(self, lt)
        self.calcDailyPivots(self, lt)
        lt = self.getFilteredData(self, lt)
        ltlen = len(lt)-1
        
        print('Full Data analysis:',fromdt, todt, ' for weekday=', self.day_to_check)
                
        self.calcDailyOpenToHighReturn(self, lt)
        self.calcDailyOpenToLowReturn(self, lt)
        print('================================================')
        
        next2Index = int(round((ltlen/3)*2, 0))
        fromdt2 = lt[next2Index][0]        
        print('1/3rd Recent Data analysis:',fromdt2, todt)
        self.calcDailyClosePPReturnRSI(self, lt[next2Index:ltlen], 0)
        self.calcDailyOpenToHighReturn(self, lt[next2Index:ltlen])
        self.calcDailyOpenToLowReturn(self, lt[next2Index:ltlen])
        #self.calcDailyATRret(self, lt[next2Index:ltlen])
        print('================================================')
        
        next3Index = int(round((ltlen/6)*5, 0))
        fromdt3 = lt[next3Index][0]        
        print('Recent Data analysis:',fromdt3, todt)
        self.calcDailyClosePPReturnRSI(self, lt[next3Index:ltlen], 0)
        self.calcDailyOpenToHighReturn(self, lt[next3Index:ltlen])
        self.calcDailyOpenToLowReturn(self, lt[next3Index:ltlen])
        #self.calcDailyATRret(self, lt[next3Index:ltlen])
        print('================================================')
        
    def calcDailyClosePPReturnRSI(self, lt, flag):
    
        last_cp = float(lt[0][4])
        dif_col = []
        ret_col = []
        count = 0
        rsi_period = 14
        for row in lt:
            dt = row[0]
            cp = float(row[4])
            dif = round(cp - last_cp,2)
            ret = round((dif/last_cp)*100,2)
                
            dif_col.append(dif)
            ret_col.append(abs(ret))            
            row.append(ret)
            if(flag == 1 and abs(ret) > self.def_ret):                
                #print('----', dt, cp, last_cp, dif)
                print(row)
            last_cp = cp
            
            #rsi calc ??? not working
            '''
            if(count > rsi_period+1):
                rsi_calc_list = dif_col[(count-rsi_period):count]
                #print(rsi_calc_list)
                #print([x for x in rsi_calc_list if x > 0])
                #print([x for x in rsi_calc_list if x < 0])
                avgUp = sum([x for x in rsi_calc_list if x > 0])/rsi_period
                avgDown = sum([abs(x) for x in rsi_calc_list if x < 0])/rsi_period
                rs = avgUp/avgDown
                rsi = round((100-(100/(1+rs))),2)
                row.append(rsi)
                #print('count:', count, ' rsi:', rsi, avgUp, avgDown, rs)
            count = count + 1
            '''
        print('calcDailyClosePPReturn:')
        print('Total count:', len(ret_col), ' from Total count', len(lt), ': average ret %:', round((sum(ret_col)/len(ret_col)),2), ' :stdev of dif:', round(statistics.stdev(dif_col),2))

    def calcDailyOpenToHighReturn(self, lt):
        print('calcDailyOpenToHighReturn:')
        self.calcGenericRet(self, lt, 1, 2, 1, 3)
        
        
    def calcDailyOpenToLowReturn(self, lt):
        print('calcDailyOpenToLowReturn:')
        self.calcGenericRet(self, lt, 1, 1, 3, 2)
        
        
    def calcDailyATRret(self, lt):
        print('calcDailyATRret:')
        self.calcGenericRet(self, lt, 1, 2, 3, 4)
        
        
    def calcGenericRet(self, lt, openP_index, highP_index, lowP_index, oppP_index):

        dif_col = []
        ret_col = []
        opp_col = []
        preret_col = []
        pa_col = []
        length = len(lt)
        for i in range(length):
            row = lt[i]
            dt_str = row[0]
            openP = float(row[openP_index])
            highP = float(row[highP_index])
            lowP = float(row[lowP_index])
            oppP = float(row[oppP_index])
            dif = round(highP - lowP,2)
            oppDif = abs(round(oppP - openP,2))
            #print(':--', dt, openP, highP, dif)
            ret = abs(round((dif/openP)*100,1))
            dt_fld = datetime.datetime.strptime(dt_str, self.frmt_str)            
                                
            if(dt_fld.weekday() == self.day_to_check):
                #and ret > self.def_ret):
                #and (oppDif < (ret/self.oppDif_sl_divisr))): 
                dif_col.append(dif)
                ret_col.append(ret)
                opp_col.append(oppDif)
                #daily returns
                preret_col.append(lt[i-1][5])
                self.pivotAnalysis(self, row, lt[i-1], pa_col)
                
            if(self.print_flag > 0 and dt_fld.year > 2018):
                    print(lt[i-1])
                    print(row)    
        #print(preret_col)
        ht_cnt = len(ret_col)
        rv_cnt = len([x for x in pa_col if 'Reversal' in x])
        tr_cnt = len([x for x in pa_col if 'Trending' in x])
        pv_cnt = len([x for x in pa_col if 'Pivot' in x])
        print('Total HT count:', len(ret_col), ' from Total count', length)
        print('count(Reversal):', rv_cnt, 'count(Trending):', tr_cnt, 'count(Pivot):', pv_cnt)
        print(': average ret %:', round((sum(ret_col)/len(ret_col)),2), ' :stdev of dif:',
              round(statistics.stdev(dif_col),2), ' :stdev of OPPdif:', round(statistics.stdev(opp_col),2),
              ' :stdev of preDay ret:', round(statistics.stdev(preret_col),2))
        
              
    def calcDailyPivots(self, lt):
        #calculate NSE pivots
        #Pivot =  High + Low + Close /3, R1 = (2*Pivot)-Low, S1= (2*Pivot)-High, R2 = Pivot+(H-L) , S2=P-(H-L)
        #'pivot'
        for row in lt:
            openP = round(float(row[1]),0)
            highP = round(float(row[2]),0)
            lowP = round(float(row[3]),0)
            closeP = round(float(row[4]),0)
            pivot = round(((highP+lowP+closeP)/3),0)
            r1 = (2*pivot) - lowP
            r2 = pivot + (highP - lowP)
            s1 = (2*pivot) - highP
            s2 = pivot - (highP - lowP)
            
            row.append(pivot)
            row.append(r1)
            row.append(r2)
            row.append(s1)
            row.append(s2)


    '''
        If open above pivot, how far reached at high
        Long Trending: open > YC/Pivot & < YDH/r1 resp.(1) and high > r2 
        Long Reversal: open < YC/Pivot(2) and high > r2 
        Long flat: ? didn't reach r2 in above conditions (1) or (2) and high < r2

        Short Trending: open > YC/Pivot(1) and high > r2 (and open-low < 1/3 of ATR (2))
        Short Reversal: open < YC/Pivot(1) and high > r2 (and open-low < 1/3 of ATR (2))
        Short flat: ? didn't reach r2 in above conditions (1) & (2) and high < r2
    '''

    def pivotAnalysis(self, row, pre_row, pa_col):
            openP = round(float(row[1]),0)
            highP = round(float(row[2]),0)
            lowP = round(float(row[3]),0)
            closeP = round(float(row[4]),0)
            yDHP = round(float(pre_row[2]),0)
            yDLP = round(float(pre_row[3]),0)
            ycP = round(float(pre_row[4]),0)            
            pivot = pre_row[6]
            r1 = pre_row[7]
            r2 = pre_row[8]
            s1 = pre_row[9]
            s2 = pre_row[10]

            analysis = 'None'
            #Long trend
            cond1 = 0
            if(openP > ycP and openP < yDHP):
                analysis = 'Open>YC'
                cond1 = 1
            if(openP > pivot and openP < r1):
                analysis = 'Open>Pivot'    
                cond1 = 1
                
            if(cond1 == 1 and highP > r2):
                analysis = 'Long Trending'

            #short trend
            cond2 = 0
            if(openP < ycP and openP > yDLP):
                analysis = 'Open<YC'
                cond2 = 1
            if(openP < pivot and openP > s1):
                analysis = 'Open<Pivot'    
                cond2 = 1
                
            if(cond2 == 1 and lowP > s2):
                analysis = 'Short Trending'

            #gapdown reversal rise
            if(cond1 == 0 and cond2 == 1 and highP > r2):
                analysis = 'Long Reversal'
                
            #gapup reversal fall
            if(cond2 == 0 and cond1 == 1 and lowP < s2):
                analysis = 'Short Reversal'

            #pa_col.append(row[0] + " : " + analysis)
            pa_col.append(analysis)
            row.append(analysis)

    
    def getFilteredData(self, lt):
        '''
            TODO
            mark the first thursday
            loop for next 5 days and find if it is a thursday,
                if it is a thursday, take it as exp d and loop for next 5 days.
            if it is friday w/o a thursday, take the previous day as exp day
        '''
        filtered_data = []
        length = len(lt)
        for i in range(length):
            row = lt[i]
            dt_str = row[0]
            dt_fld = datetime.datetime.strptime(dt_str, self.frmt_str)
            if(dt_fld.weekday() == self.day_to_check):
                #if(self.do_analysis_only == 1):
                    #filtered_data.append(lt[i-1])
                #append YD return
                row.append(lt[i-1][5])
                filtered_data.append(row)
                
                #row.append(dt_str)
                
        return filtered_data

    
    def tradeReport(self, lt):
        print('==========trade report start=======')
        fromdt = lt[0][0]
        ltlen = len(lt)-1
        todt = lt[ltlen][0]
        self.calcDailyClosePPReturnRSI(self, lt, 0)
        lt = self.getFilteredData(self, lt)        
        ltlen = len(lt)-1
        print('Full Data analysis:',fromdt, todt, ' for weekday=', self.day_to_check, 
              'self.simple_exec_flag:', self.simple_exec_flag,)
                
        self.execOptionIntraday(self, lt, 1)
        print('================================================')
        
        next2Index = int(round((ltlen/3)*2, 0))
        fromdt2 = lt[next2Index][0]        
        print('1/3rd Recent Data analysis:',fromdt2, todt)
        self.execOptionIntraday(self, lt[next2Index:ltlen], 0)
        print('================================================')
        
        next3Index = int(round((ltlen/6)*5, 0))
        fromdt3 = lt[next3Index][0]        
        print('Recent Data analysis:',fromdt3, todt)
        self.execOptionIntraday(self, lt[next3Index:ltlen], 0)
        print('================================================')

        

    def execOptionIntraday(self, lt, local_print_flag):
        self.lots_play = 1
        '''
        strategy:Long: at open buy Open+50CE @ cost:20, if  diff(open to high) > 50 , capture PnL = diff-cost , else -20 as loss.
        Short: buy open-50PE @ 20, if  diff(open to low) > 50 , capture PnL = diff-cost , else -20 as loss.
        capture both long and short independantly
        and finally together
        '''
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
        for row in lt:
            dt_str = row[0]
            dt_fld = datetime.datetime.strptime(dt_str, self.frmt_str)
            cur_yr = dt_fld.year 
           
            openP = round(float(row[1]),0)
                       
            highP = round(float(row[2]),0)
            lowP = round(float(row[3]),0)
            closeP = round(float(row[4]),0)
            YD_ret = row[len(row)-1]
            stk = round(openP,-2)
            CE_stk = stk
            PE_stk = stk
            #print('selecting', self.stk_pp_dif, ' points ITM strikes')
            CE_stk = stk - self.stk_pp_dif
            if((CE_stk - openP) > self.stk_pp_dif):
                CE_stk = stk
            
            PE_stk = stk + self.stk_pp_dif
            if((openP - PE_stk) > self.stk_pp_dif):
                PE_stk = stk

            #print('openP:', openP, ' stk:', stk, ' CE_stk:', CE_stk, ' PE_stk:', PE_stk)
                
            high_dif = highP - openP
            low_dif = openP - lowP
            
            if(self.print_flag == 1 and local_print_flag == 1):
                print(row)
                print('openP:',openP, ':CE_stk:', CE_stk, ':PE_stk:', PE_stk)
                print('high_dif:',high_dif, ':low_dif:', low_dif)
            l_ret = self.calcPnl(self, high_dif, long_pos_ret, long_neg_ret, (closeP - CE_stk), openP, CE_stk, YD_ret, 'CE')
            s_ret = self.calcPnl(self, low_dif, short_pos_ret, short_neg_ret, (PE_stk - closeP), openP, PE_stk, YD_ret, 'PE')

            #all_ret.append([dt_str, l_ret, s_ret, (l_ret+s_ret)])
            all_ret.append([dt_str, (l_ret+s_ret)])
            lpr_cnt = len(long_pos_ret)
            spr_cnt = len(short_pos_ret)
            yearly_ret = yearly_ret + l_ret + s_ret
            if(cur_yr > prev_yr):
                print('------100 points ITM stk------')
                print(row)
                print('openP:',openP, ' stk ', stk, ':CE_stk:', CE_stk, ':PE_stk:', PE_stk)
                print('high_dif:',high_dif, ':low_dif:', low_dif, 'CE closePP diff',
                      (closeP - CE_stk), 'PE close pp diff', (PE_stk - closeP), 'CE ret', l_ret, 'PE ret', s_ret)
                print('------------')
                print(cur_yr, ':- yearly ret----: ', yearly_ret)
                #print(all_ret)
                stage = stage + 1
                #self.lots_play = self.lots_play + 2
                prev_yr = cur_yr
                self.fixed_cost = self.fixed_cost + self.stage_cnt
                self.min_points_diff = self.min_points_diff + self.stage_cnt
                print('stage:', stage, ' lots play:', self.lots_play, 'self.fixed_cost:', self.fixed_cost,
                      'self.min_points_diff', self.min_points_diff)
                all_ret = []
                yearly_ret = 0
        print(all_ret)
        if(self.print_flag == 1):
            print('long_pos_ret:', long_pos_ret)
            print('long_neg_ret:', long_neg_ret)
            print('short_pos_ret:', short_pos_ret)
            print('short_neg_ret:', short_neg_ret)
            
        print('Total count:', tc, ' from Total count', tc, ' final stage:', stage,
              ' lots play:', self.lots_play, 'self.fixed_cost:', self.fixed_cost, 'self.min_points_diff', self.min_points_diff)
        lpr = len(long_pos_ret)
        lnr = len(long_neg_ret)
        spr = len(short_pos_ret)
        snr = len(short_neg_ret)
        print('count(long_pos_ret):', lpr, ' sum(lpr)', sum(long_pos_ret),
              ' count(long_neg_ret):', lnr, 'sum(lnr)', sum(long_neg_ret),
              'count(short_pos_ret):', spr, 'sum(spr)', sum(short_pos_ret),
              'count(short_neg_ret):', snr, 'sum(snr)', sum(short_neg_ret),)
        print(': average long ret :', round(((sum(long_pos_ret)+sum(long_neg_ret))/(lpr+lnr)),2),
              ' :stdev of LPR:', round(statistics.stdev(long_pos_ret),2),
              ': average short ret :', round(((sum(short_pos_ret)+sum(short_neg_ret))/(spr+snr)),2),
              ' :stdev of SPR:', round(statistics.stdev(short_pos_ret),2)
              )
        comb_pos_ret = long_pos_ret + short_pos_ret
        comb_neg_ret = long_neg_ret + short_neg_ret
        print(':Combined Positive ret avg:', round(((sum(comb_pos_ret))/(lpr+spr)),2),
              ' :stdev of comb pos:', round(statistics.stdev(comb_pos_ret),2),
              ': Overall Total avg ret :', round(((sum(comb_pos_ret)+sum(comb_neg_ret))/tc),2),
              ' :stdev of overall:', round(statistics.stdev((comb_pos_ret+comb_neg_ret)),2) ,
              ' :Overall Total ret:', (sum(comb_pos_ret)+sum(comb_neg_ret)) 
              )
        
        
        
    '''
    Execution varation, 1 lot, 2 lot, 3 lot with 10-50% gain exit, 50% SL, 2nd lot max exit at STD dev, or at close PP.
    stdev of long +ve ret = 40, stdev of short +ve ret = 70
    '''
   
    
    def calcPnl(self, diff, pos_ret, neg_ret, closePP_diff, openP, stk, YD_ret, CE_PE):
        #print('calcPnl:0', diff)
        pnl = 0
        pnl_1 = 0
        pnl_2 = 0
        cost = self.calcCost(self, openP, stk, YD_ret, CE_PE)
        #simple exec, go for high/low PP diff - min_diff, (difficult to execute)    
        if(self.simple_exec_flag == 1):
            #print('calcPnl:1', diff)
            if(diff > self.stk_pp_dif):
                pnl = ((diff - cost)-(self.min_points_diff)) * self.lots_play
                pos_ret.append(pnl)          
            else:
                pnl = (0 - (cost/self.min_sl_divisr)) * self.lots_play
                neg_ret.append(pnl)
                
            if(self.print_flag == 1):    
                print('calcPnl:1', 'diff', diff, 'closePP_diff', closePP_diff, 'total pnl ', pnl,
                      'spot', openP, 'strike', stk, 'YDret', YD_ret, 'prem', cost, CE_PE)     
        elif(self.simple_exec_flag == 2):
            #??
            if(diff > (self.min_points_diff)):
                #1st lot at 20% of fixed cost so at least 10 points+fixed cost, so 10 Rs. self.min_points_diff
                pnl_1 = self.min_points_diff
                #2nd lot at 50% higher 
                if(diff > (cost * (self.max_pnl_perc))):
                    pnl_2 = ((cost * (self.max_pnl_perc)) - cost) * (self.lots_play-1)
                else:
                    #exit at 50% stop loss
                    pnl_2 = (0 - (cost/self.min_sl_divisr)) * (self.lots_play-1)
                pnl = pnl_1 + pnl_2
                pos_ret.append(pnl)
            else:
                 #exit at 50% stop loss, 2nd lot at full loss
                pnl_1 = (0 - (cost/self.min_sl_divisr))
                pnl_2 = (0 - (cost/self.min_sl_divisr)) * (self.lots_play-1)
                pnl = pnl_1 + pnl_2
                neg_ret.append(pnl)
                
            if(self.print_flag == 1):    
                print('calcPnl:2', 'diff', diff, 'closePP_diff', closePP_diff, 'pnl_1', pnl_1, 'pnl_2', pnl_2, 'total pnl ', pnl,
                      'spot', openP, 'strike', stk, 'YDret', YD_ret, 'prem', cost, CE_PE)    
        elif(self.simple_exec_flag == 3):
            if(closePP_diff > cost):
                pnl = (closePP_diff - cost) * self.lots_play
                pos_ret.append(pnl)
            elif(closePP_diff < cost and closePP_diff > 2):
                pnl = (closePP_diff - cost) * self.lots_play
                neg_ret.append(pnl)
            elif(closePP_diff < 2):
                if(diff < self.min_points_diff):
                    pnl = (0 - cost/self.min_sl_divisr) * self.lots_play
                    neg_ret.append(pnl)
                else:
                    pnl = (0 - cost) * self.lots_play
                    neg_ret.append(pnl)

            if(self.print_flag == 1):    
                print('calcPnl:3', 'diff', diff, 'closePP_diff', closePP_diff, ' pnl ', pnl,
                      'spot', openP, 'strike', stk, 'YDret', YD_ret, 'prem', cost, CE_PE)
                
        return pnl

    def calcTodaysCE(self, openP):

         stk = round(openP,-2)
         exp_highP = openP + self.long_max_exit_stddev
         
         CE_stk = stk
         '''
         print('selecting ', self.stk_pp_dif,' points ', self.ITM_OTM,  ' strikes')
         if(self.ITM_OTM == 'ITM'):             
             CE_stk = stk - self.stk_pp_dif
         elif(self.ITM_OTM == 'OTM'):             
             CE_stk = stk + self.stk_pp_dif
         elif(self.ITM_OTM == 'ATM'):             
             CE_stk = stk 
         '''    
         if((exp_highP - CE_stk) < self.stk_pp_dif):
             CE_stk = stk - self.stk_pp_dif

         print('openP:', openP, ' stk:', stk, ' CE_stk:', CE_stk, 'exp_highP', exp_highP, 'diff', (exp_highP - CE_stk))

    def calcCost(self, spot, stk, YD_ret, CE_PE):
        #print('calcCost: CE_stk', CE_stk, 'PE_stk', PE_stk)
        CE_volt = self.default_volt
        PE_volt = self.default_volt + self.high_volt_ret
        if(YD_ret >= self.high_volt_ret):
            CE_volt = CE_volt + self.high_volt_ret
            PE_volt = PE_volt + self.high_volt_ret
        elif(YD_ret >= self.low_volt_ret):
            CE_volt = CE_volt - self.low_volt_ret
            PE_volt = PE_volt - self.low_volt_ret

        if(CE_PE == 'CE'):    
            prem = self.calcPrem(self, spot, stk, 1, CE_volt, 'CE')
        elif(CE_PE == 'PE'):    
            prem = self.calcPrem(self, spot, stk, 1, PE_volt, 'PE')

        return prem    
        

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

def main():
    dInst = DailyDataAnalyser
    dInst.readOHLCDataFile(dInst, 'C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\NSE_Index_data.csv');

if __name__=="__main__":
    msg = main()
