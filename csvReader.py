import csv
import statistics
'''
version1: read bhavcopy files of last 2 days and today live stock data file and mearge in a list and print.
version1.1: collect data in a map. with stokname as a key and two day historical data + live data as list for the stock.
version2: StrategyBuilder with 2DH BO bullish strategy coded and verified actual run.
version2.1: Nifty index dataanalystics added. (23-July-2021)
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
##        print('Total count:', len(ret_col), ': average ret %--', round((sum(ret_col)/len(ret_col)),2), 'stdev of dif--', round(statistics.stdev(dif_col),2))


    def readNiftyIndexDataFile(self, fileName):

        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            print('Date, Close Price')
            lt = list(reader)
            del lt[0]
            self.dataAnalytics(self, lt)
           

    def dataAnalytics(self, lt):
        fromdt = lt[0][0]
        ltlen = len(lt)-1
        todt = lt[ltlen][0]
        print('Full Data analysis:',fromdt, todt)
        
        self.calcDailyClosePPReturn(self, lt)
        self.calcDailyOpenToHighReturn(self, lt)
        self.calcDailyOpenToLowReturn(self, lt)
        self.calcDailyATRret(self, lt)

        next2Index = int(round((ltlen/3)*2, 0))
        fromdt2 = lt[next2Index][0]        
        print('1/3rd Recent Data analysis:',fromdt2, todt)
        self.calcDailyClosePPReturn(self, lt[next2Index:ltlen])
        self.calcDailyOpenToHighReturn(self, lt[next2Index:ltlen])
        self.calcDailyOpenToLowReturn(self, lt[next2Index:ltlen])
        self.calcDailyATRret(self, lt[next2Index:ltlen])

        next3Index = int(round((ltlen/5)*4, 0))
        fromdt3 = lt[next3Index][0]        
        print('Recent Data analysis:',fromdt3, todt)
        self.calcDailyClosePPReturn(self, lt[next3Index:ltlen])
        self.calcDailyOpenToHighReturn(self, lt[next3Index:ltlen])
        self.calcDailyOpenToLowReturn(self, lt[next3Index:ltlen])
        self.calcDailyATRret(self, lt[next3Index:ltlen])
        
        
    def calcDailyClosePPReturn(self, lt):
    
        last_cp = float(lt[0][4])
        dif_col = []
        ret_col = []
        for row in lt:
            dt = row[0]
            cp = float(row[4])
            dif = round(cp - last_cp,2)
            #print('----', dt, cp, last_cp, dif)
            ret = round((dif/last_cp)*100,1)
                
            dif_col.append(dif)
            ret_col.append(abs(ret))
            last_cp = cp
            
        print('calcDailyClosePPReturn:')
        print('Total count:', len(ret_col), ': average ret %--', round((sum(ret_col)/len(ret_col)),2), 'stdev of dif--', round(statistics.stdev(dif_col),2))

    def calcDailyOpenToHighReturn(self, lt):
        print('calcDailyOpenToHighReturn:')
        self.calcGenericRet(self, lt, 1, 2, 1)
        
        
    def calcDailyOpenToLowReturn(self, lt):
        print('calcDailyOpenToLowReturn:')
        self.calcGenericRet(self, lt, 1, 1, 3)
        
        
    def calcDailyATRret(self, lt):
        print('calcDailyATRret:')
        self.calcGenericRet(self, lt, 1, 2, 3)
        
        
    def calcGenericRet(self, lt, index_1, index_2, index_3):

        dif_col = []
        ret_col = []                
        for row in lt:
            dt = row[0]
            openP = float(row[index_1])
            highP = float(row[index_2])
            lowP = float(row[index_3])
            dif = round(highP - lowP,2)
            #print('----', dt, openP, highP, dif)
            ret = round((dif/openP)*100,1)
                
     
            dif_col.append(dif)
            ret_col.append(abs(ret))
            
        print('Total count:', len(ret_col), ': average ret %--', round((sum(ret_col)/len(ret_col)),2), 'stdev of dif--', round(statistics.stdev(dif_col),2))
        
