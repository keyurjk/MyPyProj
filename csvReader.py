import csv
import statistics
'''
version1: read bhavcopy files of last 2 days and today live stock data file and mearge in a list and print.
version1.1: collect data in a map. with stokname as a key and two day historical data + live data as list for the stock.
version2: StrategyBuilder with 2DH BO bullish strategy coded and verified actual run.
version2.1: Nifty index dataanalystics added. (23-July-2021)
version2.2: Added Open To High and Low analysis. With open > YC/Pivot. 
version3: TODO 1. To livetest, afternoon data and EOD data. 2. generate report.
            3. Improve on Entry exit. (halfway entry, SL-calc first and calculate Target based on SL and if matching Daily pivot.
            4. Improve execution by adding QTY to profitable trades and reducing for losing.
            5. Also book profit at 1% gain from entry or (2% gain of stock) or R2 touch.
version4: TODO Modify for backtest data of last one year.

'''

class StrategyTester:
    
    tradeSignalData=''    

    def populate(self, itradeSignalData):
        print("populate")
        self.tradeSignalData = itradeSignalData
        
    def collectLiveStockData(self, fileReader, fileName):
        mappingKeys = list(self.tradeSignalData)
        fileReader.readLiveStocksDataFile(self, fileName, mappingKeys, self.tradeSignalData)

    def test2DHCrossBullishStrategy(self):
        mappingKeys = list(self.tradeSignalData)
        for stock in mappingKeys:
            print('stockKey:', stock)
            data = self.tradeSignalData[stock]
            print('BODdata', data[0])            
            epp = float(data[0][1].replace(',',''))
            slp = float(data[0][2].replace(',',''))
            #print('Live data', data[1])
            ltp = float(data[1][5].replace(',',''))
            dlp = float(data[1][3].replace(',',''))
            pos_cond = ''
            neg_cond = ''
            result = [stock]
            if(ltp>epp):
                pos_cond = 'SUCCESS'
                result.append(pos_cond)
                result.append(ltp)
            if(dlp<slp):
                neg_cond = 'FAILED'
                result.append(neg_cond)
                result.append(ltp)
            data.append(result)
            #print('=========TEST REPORT ======'
            print(result)
    
'''
----------------
'''
class StrategyBuilder:

    selectedStocksData=''
    tradeSignalData=dict()
    def populate(self, iselectedStocksData):
        print("populate")
        self.selectedStocksData = iselectedStocksData
        
    def generateTradeSignal(self):
        print("generateTradeSignal")        
        self.strategy2DHCrossBullish(self)
        print("-------------------\n-------------")
        #print(self.tradeSignalData)

    def strategy2DHCrossBullish(self):
        #strategyCode
        mappingKeys = list(self.selectedStocksData)
        for stock in mappingKeys:
            #?print('stockKey:', stock)
            data = self.selectedStocksData[stock]
            #(already sorted while insertion, last first)
            #?print("data::", len(data))
            if(len(data)==3):
                opp = float(data[2][1].replace(',',''))
                dhp = float(data[2][2].replace(',',''))
                ycp = float(data[2][4].replace(',',''))
                ltp = float(data[2][5].replace(',',''))                
                
                
                d1h = float(data[0][3].replace(',',''))
                d2h = float(data[1][3].replace(',',''))
                maxdh = max(d1h, d2h)
                #?print("opp:", opp, "ltp:", ltp, "dhp:", dhp, "ycp:", ycp, "d1h:", d1h,"d2h:", d2h, "maxdh:", maxdh)
                if((dhp > maxdh) & (ltp > ycp) & (ltp > opp)):
                    self.tradeSignalData[stock] = []
                    (self.tradeSignalData[stock]).append(['BOD',data[2][5],data[2][3],'T1?'])
                   
        
'''
----------------
'''        
class FileReader:

    selectedStocksData = dict()
    
    def readDailyBhavCopy(self, bhavFileName, selectedStocksList, selectedStocksData):
        with open(bhavFileName, newline='') as f:
            reader = csv.reader(f)
            print('reading bhavFileName:', bhavFileName)
            lt = list(reader)
            print(lt[0])
            
            for row in lt:
                stock = row[0]
                if((stock in selectedStocksList) & (row[1]=='EQ')):
                    (selectedStocksData[stock]).append(row)
                    #print(row)

    def collectSelectedStocksData(self, liveFileName, bhavFileName3, bhavFileName2, bhavFileName1, selectedStocksFile):
        selectedStocksList = set([])
        selectedStocksData = self.selectedStocksData
        print('file:', selectedStocksFile)
        with open(selectedStocksFile, newline='') as f1:
            reader1 = csv.reader(f1)
            print('selectedStocksFile:', selectedStocksFile)
            lt1 = list(reader1)
            del lt1[0]           
            for row in lt1:
                stock = row[0]
                selected = row[1]
                if(selected=='Y'):
                    selectedStocksList.add(stock)
                    selectedStocksData[stock]=[]
        if(bhavFileName3!=''):
            self.readDailyBhavCopy(self, bhavFileName3, selectedStocksList, selectedStocksData)
        if(bhavFileName2!=''):
            self.readDailyBhavCopy(self, bhavFileName2, selectedStocksList, selectedStocksData)
        if(bhavFileName1!=''):
            self.readDailyBhavCopy(self, bhavFileName1, selectedStocksList, selectedStocksData)
        if(liveFileName!=''):        
            self.readLiveStocksDataFile(self, liveFileName, selectedStocksList, selectedStocksData)

        print('completed reading all files:Y')    
        print('selectedStocksData:', len(selectedStocksData))
        #selectedStocksData.sort()
        #for row in selectedStocksData:
        #?print(selectedStocksData)

    
    
    def readLiveStocksDataFile(self, fileName, selectedStocksList, selectedStocksData):
        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            print('reading LiveStocksDataFile:', fileName)
            lt = list(reader)
            print(lt[0])
            
            for row in lt:
                #print(row)
                stock = row[0]
                if((stock in selectedStocksList)):
                    (selectedStocksData[stock]).append(row)
                    #print('added')
    
    def readHistoricalStockFile(self, fileName):

        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            print('Date, Close Price')
            lt = list(reader)
            del lt[0]
            last_cp = 1
            for row in reversed(lt):
                dt = row[0]
                cp = float(row[8])
                dif = round(cp - last_cp,4)
                #print('----', dt, cp, last_cp, dif)
                ret = round(dif*100,1)
                last_cp = cp
                row[6] = round(dif,2)
                row[7] = ret
                row[8] = cp
                #print(dt, cp, row[6], row[7], '%')

##        ret_col = [col[7] for col in lt]
##        dif_col = [col[8] for col in lt]
##        print('Total count:', len(ret_col), ': average ret %--', round((sum(ret_col)/len(ret_col)),2), ' :stdev of dif--', round(statistics.stdev(dif_col),2))


    def_ret = 1
    def readNiftyIndexDataFile(self, fileName):

        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            print('Date, Close Price')
            lt = list(reader)
            del lt[0]
            self.dataAnalytics(self, lt)
           

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
        
        print('Full Data analysis:',fromdt, todt)
        
        self.calcDailyClosePPReturnRSI(self, lt)
        #self.calcDailyATRret(self, lt)
        self.calcDailyPivots(self, lt)
        self.calcDailyOpenToHighReturn(self, lt)
        self.calcDailyOpenToLowReturn(self, lt)
        #print(lt[ltlen-10:ltlen])
        
        next2Index = int(round((ltlen/3)*2, 0))
        fromdt2 = lt[next2Index][0]        
        print('1/3rd Recent Data analysis:',fromdt2, todt)
        self.calcDailyClosePPReturnRSI(self, lt[next2Index:ltlen])
        self.calcDailyOpenToHighReturn(self, lt[next2Index:ltlen])
        self.calcDailyOpenToLowReturn(self, lt[next2Index:ltlen])
        #self.calcDailyATRret(self, lt[next2Index:ltlen])

        next3Index = int(round((ltlen/6)*5, 0))
        fromdt3 = lt[next3Index][0]        
        print('Recent Data analysis:',fromdt3, todt)
        self.calcDailyClosePPReturnRSI(self, lt[next3Index:ltlen])
        self.calcDailyOpenToHighReturn(self, lt[next3Index:ltlen])
        self.calcDailyOpenToLowReturn(self, lt[next3Index:ltlen])
        #self.calcDailyATRret(self, lt[next3Index:ltlen])
        
        
    def calcDailyClosePPReturnRSI(self, lt):
    
        last_cp = float(lt[0][4])
        dif_col = []
        ret_col = []
        count = 0
        rsi_period = 14
        for row in lt:
            dt = row[0]
            cp = float(row[4])
            dif = round(cp - last_cp,2)
            #print('----', dt, cp, last_cp, dif)
            ret = round((dif/last_cp)*100,2)
                
            dif_col.append(dif)
            ret_col.append(abs(ret))
            last_cp = cp
            row.append(ret)
            
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
        print('Total count:', len(ret_col), ': average ret %:', round((sum(ret_col)/len(ret_col)),2), ' :stdev of dif:', round(statistics.stdev(dif_col),2))

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
            dt = row[0]
            openP = float(row[openP_index])
            highP = float(row[highP_index])
            lowP = float(row[lowP_index])
            oppP = float(row[oppP_index])
            dif = round(highP - lowP,2)
            oppDif = abs(round(oppP - openP,2))
            #print(':--', dt, openP, highP, dif)
            ret = abs(round((dif/openP)*100,1))
            
            if(ret > self.def_ret): 
                dif_col.append(dif)
                ret_col.append(ret)
                opp_col.append(oppDif)
                #daily returns
                preret_col.append(lt[i-1][5])
                self.pivotAnalysis(self, row, lt[i-1], pa_col)
                
        #print(preret_col)
        ht_cnt = len(ret_col)
        rv_cnt = len([x for x in pa_col if x == 'Reversal'])
        tr_cnt = len([x for x in pa_col if x == 'Trending'])
        pv_cnt = len([x for x in pa_col if x == 'Trending'])
        print('Total HT count:', len(ret_col), ': average ret %:', round((sum(ret_col)/len(ret_col)),2), ' :stdev of dif:', round(statistics.stdev(dif_col),2), ' :stdev of OPPdif:', round(statistics.stdev(opp_col),2), ' :stdev of preDay ret:', round(statistics.stdev(preret_col),2))
        print('count(Reversal):', rv_cnt, 'count(Trending):', tr_cnt, 'count(Pivot):', pv_cnt)
              
    def calcDailyPivots(self, lt):
        #calculate NSE pivots
        #Pivot =  High + Low + Close /3, R1 = (2*Pivot)-Low, S1= (2*Pivot)-High, R2 = Pivot+(H-L) , S2=P-(H-L)
        #'pivot'
        for row in lt:
            openP = round(float(row[1]),0)
            highP = round(float(row[2]),0)
            lowP = round(float(row[3]),0)
            closeP = round(float(row[4]),0)
            pivot = round(((openP+highP+closeP)/3),0)
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
            #rise trend
            cond1 = 0
            if(openP > ycP and openP < yDHP):
                analysis = 'Open>YC'
                cond1 = 1
            if(openP > pivot and openP < r1):
                analysis = 'Open>Pivot'    
                cond1 = 1
                
            if(cond1 == 1 and highP > r2):
                analysis = 'Trending'

            #fall trend
            cond2 = 0
            if(openP < ycP and openP > yDLP):
                analysis = 'Open<YC'
                cond2 = 1
            if(openP < pivot and openP > s1):
                analysis = 'Open<Pivot'    
                cond2 = 1
                
            if(cond2 == 1 and lowP > s2):
                analysis = 'Trending'

            #gapdown reversal rise
            if(cond1 == 0 and highP > r2):
                analysis = 'Reversal'
                
            #gapup reversal fall
            if(cond2 == 0 and lowP < s2):
                analysis = 'Reversal'

            #pa_col.append(row[0] + " : " + analysis)
            pa_col.append(analysis)   
        
