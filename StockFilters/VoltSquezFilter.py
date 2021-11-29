import csv, statistics, datetime
#import os, urllib.request, concurrent.futures  
'''
version1: read bhavcopy files of last 4 days and today live stock data file and mearge in a list and print.
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


    
'''
----------------
'''
class VoltSqzStrategyBuilder:

    selectedStocksData=''
    filteredStocks=''
    tradeSignalData=dict()

    def populate(self, iselectedStocksData):
        self.populate(self, iselectedStocksData, '')
        
    def populate(self, iselectedStocksData, iFilteredStocks):
        print("populate")
        self.selectedStocksData=''
        self.selectedStocksData = iselectedStocksData
        self.filteredStocks=''
        self.filteredStocks = iFilteredStocks
        
    def generateTradeSignal(self):
        print("generateTradeSignal")        
        self.filterVoltSquezStocks(self)
        print("-------------------\n-------------")
        print('VoltSquezStocks')
        print(self.tradeSignalData)
        

    def backTest(self):
        print("backTest")        

    def filterVoltSquezStocks(self):
        '''
            logic is check ATR of last 4  days, after 2 days check if ATR decreased by > 50%
            select that stock
        '''
        mappingKeys = ''
        if(self.filteredStocks == ''):            
            mappingKeys = list(self.selectedStocksData)
        else:
            mappingKeys = list(self.filteredStocks)
            
        for stock in mappingKeys:
            print('VSF: stockKey:', stock)
            data = self.selectedStocksData[stock]
            #(already sorted while insertion, last first)
            
            datalen = len(data)
            #print(stock, " datalen::", datalen)
            if(datalen>=4):
                dOP1 = float(data[0][2].replace(',',''))
                dHP = float(data[0][3].replace(',',''))
                dLP = float(data[0][4].replace(',',''))
                dCP1 = float(data[0][5].replace(',',''))
                atrD1 = dHP - dLP
                #opcl1 = abs(dOP1-dCP1)

                dOP2 = float(data[1][2].replace(',',''))
                dHP = float(data[1][3].replace(',',''))
                dLP = float(data[1][4].replace(',',''))
                dCP2 = float(data[1][5].replace(',',''))
                atrD2 = dHP - dLP
                ret1 = round(((dCP2 - dCP1)/dCP1)*100,2)
                #opcl2 = abs(dOP2-dCP2)
                
                dOP3 = float(data[2][2].replace(',',''))
                dHP = float(data[2][3].replace(',',''))
                dLP = float(data[2][4].replace(',',''))
                dCP3 = float(data[2][5].replace(',',''))
                atrD3 = dHP - dLP
                ret2 = round(((dCP3 - dCP2)/dCP2)*100,2)
                #opcl3 = abs(dOP3-dCP3)
                
                dOP4 = float(data[3][2].replace(',',''))
                dHP = float(data[3][3].replace(',',''))
                dLP = float(data[3][4].replace(',',''))
                dCP4 = float(data[3][5].replace(',',''))
                atrD4 = dHP - dLP                
                ret3 = round(((dCP4 - dCP3)/dCP3)*100,2)
                #opcl4 = abs(dOP4-dCP4)
                if(atrD4 == 0):
                    atrD4 = 0.01               
                totalret = ret1 + ret2 + ret3
                genre = data[datalen-1]
                maxsqz = max((atrD3/atrD4),(atrD2/atrD4),(atrD1/atrD4))
                if ((maxsqz > 2) and (atrD4 < atrD3) and (totalret > 4 or totalret < -4)):
                    #print("data:",data)
                    print("ATRS:",stock, atrD1, atrD2, atrD3, atrD4)
                    print("DCP:", stock, dCP1, dCP2, dCP3, dCP4)
                    print("returns:", stock, ret1, ret2, ret3)
                    print(data)
                    self.tradeSignalData[stock] = []
                    (self.tradeSignalData[stock]).append(['EOD: YDH : YDL',dHP,dLP, 'ATR-SQZ', round(maxsqz,2), round(totalret,2),'%', genre])
                    
                '''
                if ((opcl3/opcl4) > 1.8 or (opcl2/opcl4) > 1.8 or (opcl1/opcl4) > 1.8):
                    print("OP-CL-Range:",stock, opcl1, opcl2, opcl3, opcl4)
                    if(stock not in self.tradeSignalData):
                        self.tradeSignalData[stock] = []
                        
                    (self.tradeSignalData[stock]).append(['EOD: YDO : YDC',dOP4,dCP4, 'OP-CL-SIGNAL', maxret, minret, resultdate])
                
                #today's data
                lopp = float(data[4][1].replace(',',''))
                ldhp = float(data[4][2].replace(',',''))
                ldlp = float(data[4][3].replace(',',''))
                ltp = float(data[4][5].replace(',',''))                
                ycp = float(data[4][4].replace(',',''))
                
                d1h = float(data[2][3].replace(',',''))
                d2h = float(data[3][3].replace(',',''))
                mindh = min(d1h, d2h)
                d1l = float(data[2][4].replace(',',''))
                d2l = float(data[3][4].replace(',',''))
                maxdl = max(d1l, d2l)
                #?print("opp:", opp, "ltp:", ltp, "dhp:", dhp, "ycp:", ycp, "d1h:", d1h,"d2h:", d2h, "maxdh:", maxdh)
                if((ldhp > mindh)):
                    self.tradeSignalData[stock] = []
                    (self.tradeSignalData[stock]).append(['BOD:Entry:SL',mindh,ycp,'BULLISH'])
                if((ldlp < maxdl)):
                    self.tradeSignalData[stock] = []
                    (self.tradeSignalData[stock]).append(['BOD:Entry:SL',maxdl,ycp,'BEARISH'])    
                '''
                
'''
----------------
'''        
class VoltSqzFileReader:

    selectedStocksData = dict()
    
    def readDailyBhavCopy(self, bhavFileName, selectedStocksList, selectedStocksData):
        with open(bhavFileName, newline='') as f:
            reader = csv.reader(f)
            print('reading bhavFileName:', bhavFileName)
            lt = list(reader)
            #print(lt[0])
            
            for row in lt:
                stock = row[0]
                if((stock in selectedStocksList) & (row[1]=='EQ')):
                    (selectedStocksData[stock]).append(row)
                    #print(row)

    def collectSelectedStocksData(self, liveFileName, bhavFileName4, bhavFileName3, bhavFileName2, bhavFileName1, selectedStocksFile):
        selectedStocksList = set([])
        selectedStocksData = self.selectedStocksData
        print('file:', selectedStocksFile)
        with open(selectedStocksFile, newline='') as f1:
            reader1 = csv.reader(f1)
            #print('selectedStocksFile:', selectedStocksFile)
            lt1 = list(reader1)
            del lt1[0]           
            for row in lt1:
                stock = row[0]
                selectedStocksList.add(stock)
                selectedStocksData[stock]=[]

        #Pre-3-DB4-YD file            
        if(bhavFileName4!=''):
            self.readDailyBhavCopy(self, bhavFileName4, selectedStocksList, selectedStocksData)
        #Pre-2-DB4-YD file
        if(bhavFileName3!=''):
            self.readDailyBhavCopy(self, bhavFileName3, selectedStocksList, selectedStocksData)
        #DB4-YD file
        if(bhavFileName2!=''):
            self.readDailyBhavCopy(self, bhavFileName2, selectedStocksList, selectedStocksData)
        #YD file
        if(bhavFileName1!=''):
            self.readDailyBhavCopy(self, bhavFileName1, selectedStocksList, selectedStocksData)
        #if(liveFileName!=''):        
        #    self.readLiveStocksDataFile(self, liveFileName, selectedStocksList, selectedStocksData)


        with open(selectedStocksFile, newline='') as f1:
            reader1 = csv.reader(f1)
            #print('selectedStocksFile:', selectedStocksFile)
            lt1 = list(reader1)
            del lt1[0]           
            for row in lt1:
                stock = row[0]
                genre = row[1]                
                (selectedStocksData[stock]).append(genre)    

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
                stock = row[0]
                if((stock in selectedStocksList)):
                    (selectedStocksData[stock]).append(row)
                    #print(row)
    
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

 
           
