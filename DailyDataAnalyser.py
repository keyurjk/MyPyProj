import csv, statistics, datetime
#import os, urllib.request, concurrent.futures  
'''
version1.1: Nifty index dataanalystics added. (23-July-2021)
version1.2: Added Open To High and Low analysis. With open > YC/Pivot.
version1.3: Analyse particular day of week. 
version1.4: Execution varation, 1 lot, 2 lot, 3 lot with 10-50% gain exit, 50% SL, 2nd lot max exit at STD dev, or at close PP.
'''
class DailyDataAnalyser:

    def_ret = 1
    oppDif_sl_divisr = 3
    frmt_str = '%d/%m/%Y'
    #thursday
    day_to_check = 3
    print_flag = 0
    do_analysis_only = 0
    backtest_trading_strategy = 0
    fixed_cost = 45
    simple_exec_flag = 3
    lots_play = 2
    stk_pp_dif = 50

    min_points_diff = 10
    max_pnl_perc = 1.5
    min_sl_divisr = 2
    long_max_exit_stddev = 40
    short_max_exit_stddev = 70
    
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
                                
            if(dt_fld.weekday() == self.day_to_check and ret > self.def_ret):
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
                if(self.do_analysis_only == 1):
                    filtered_data.append(lt[i-1])

                filtered_data.append(row)
                
                #row.append(dt_str)
                
        return filtered_data

    
    def tradeReport(self, lt):
        print('==========trade report start=======')
        fromdt = lt[0][0]
        ltlen = len(lt)-1
        todt = lt[ltlen][0]
        lt = self.getFilteredData(self, lt)        
        ltlen = len(lt)-1
        print('Full Data analysis:',fromdt, todt, ' for weekday=', self.day_to_check, 
              'self.simple_exec_flag:', self.simple_exec_flag, ' cost*1.5:', (self.fixed_cost * self.max_pnl_perc))
                
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
        self.lots_play = 2
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
        stage = 10
        for row in lt:
            dt_str = row[0]
            
            exec_cnt = exec_cnt + 1
            openP = round(float(row[1]),0)
                       
            highP = round(float(row[2]),0)
            lowP = round(float(row[3]),0)
            closeP = round(float(row[4]),0)
            stk = round(openP,-2)
            CE_stk = stk
            PE_stk = stk
            #selecting 50 points OTM strikes
            #if(stk < openP):
            CE_stk = stk - self.stk_pp_dif
            #if(stk > openP):
            PE_stk = stk + self.stk_pp_dif
                
            high_dif = highP - openP
            low_dif = openP - lowP
            
            if(self.print_flag == 1 and local_print_flag == 1):
                print(row)
                print('openP:',openP, ':CE_stk:', CE_stk, ':PE_stk:', PE_stk)
                print('high_dif:',high_dif, ':low_dif:', low_dif)
            l_ret = self.calcPnl(self, high_dif, long_pos_ret, long_neg_ret, (closeP - CE_stk))
            s_ret = self.calcPnl(self, low_dif, short_pos_ret, short_neg_ret, (PE_stk - closeP))

            #all_ret.append([dt_str, l_ret, s_ret, (l_ret+s_ret)])
            all_ret.append([dt_str, (l_ret+s_ret)])
            lpr_cnt = len(long_pos_ret)
            spr_cnt = len(short_pos_ret)
            if(lpr_cnt > stage or spr_cnt > stage):
                print('stage surpassed:', stage, 'self.lots_play', self.lots_play)
                stage = stage + 10
                self.lots_play = self.lots_play + 2

        if(self.print_flag == 1):
            print('long_pos_ret:', long_pos_ret)
            print('long_neg_ret:', long_neg_ret)
            print('short_pos_ret:', short_pos_ret)
            print('short_neg_ret:', short_neg_ret)
            
        print('Total count:', tc, ' from Total count', tc)
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
        print(all_ret)

    '''
    Execution varation, 1 lot, 2 lot, 3 lot with 10-50% gain exit, 50% SL, 2nd lot max exit at STD dev, or at close PP.
    stdev of long +ve ret = 40, stdev of short +ve ret = 70
    '''
   
    
    def calcPnl(self, diff, pos_ret, neg_ret, closePP_diff):
        #print('calcPnl:0', diff)
        pnl = 0
        pnl_1 = 0
        pnl_2 = 0
        if(self.simple_exec_flag == 1):
            #print('calcPnl:1', diff)
            if(diff > self.stk_pp_dif):
                pnl = ((diff - self.fixed_cost)-(self.min_points_diff)) * self.lots_play
                pos_ret.append(pnl)          
            else:
                pnl = (0 - (self.fixed_cost/self.min_sl_divisr)) * self.lots_play
                neg_ret.append(pnl)
                
            if(self.print_flag == 1):    
                print('calcPnl:1', diff, closePP_diff, 'total pnl ', pnl)     
        elif(self.simple_exec_flag == 2):
            #??
            if(diff > (self.min_points_diff)):
                #1st lot at 20% of fixed cost so at least 10 points+fixed cost, so 10 Rs. self.min_points_diff
                pnl_1 = self.min_points_diff
                #2nd lot at 50% higher 
                if(diff > (self.fixed_cost * (self.max_pnl_perc))):
                    pnl_2 = ((self.fixed_cost * (self.max_pnl_perc)) - self.fixed_cost) * (self.lots_play-1)
                else:
                    #exit at 50% stop loss
                    pnl_2 = (0 - (self.fixed_cost/self.min_sl_divisr)) * (self.lots_play-1)
                pnl = pnl_1 + pnl_2
                pos_ret.append(pnl)
            else:
                 #exit at 50% stop loss, 2nd lot at full loss
                pnl_1 = (0 - (self.fixed_cost/self.min_sl_divisr))
                pnl_2 = (0 - (self.fixed_cost/self.min_sl_divisr)) * (self.lots_play-1)
                pnl = pnl_1 + pnl_2
                neg_ret.append(pnl)
                
            if(self.print_flag == 1):    
                print('calcPnl:2', diff, pnl_1, pnl_2, 'total pnl ', pnl)    
        elif(self.simple_exec_flag == 3):
            if(closePP_diff > self.fixed_cost):
                pnl = (closePP_diff - self.fixed_cost) * self.lots_play
                pos_ret.append(pnl)
            elif(closePP_diff < self.fixed_cost and closePP_diff > 2):
                pnl = (closePP_diff - self.fixed_cost) * self.lots_play
                neg_ret.append(pnl)
            elif(closePP_diff < 2):
                if(diff < self.min_points_diff):
                    pnl = (0 - self.fixed_cost/self.min_sl_divisr) * self.lots_play
                    neg_ret.append(pnl)
                else:
                    pnl = (0 - self.fixed_cost) * self.lots_play
                    neg_ret.append(pnl)

            if(self.print_flag == 1):    
                print('calcPnl:3', diff, closePP_diff, ' pnl ', pnl)
                
        return pnl
