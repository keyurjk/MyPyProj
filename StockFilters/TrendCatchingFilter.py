import csv, statistics, datetime
#import os, urllib.request, concurrent.futures  
'''
version1: read bhavcopy files of last 4 days and today live stock data file and mearge in a list and print.
version1.1: collect data in a map. with stokname as a key and two day historical data + live data as list for the stock.


'''


    
'''
----------------
'''
class StrategyBuilder:

    selectedStocksData=''
    tradeSignalData=dict()
    def populate(self, iselectedStocksData):
        print("populate")
        self.selectedStocksData=''
        self.selectedStocksData = iselectedStocksData
        
    def generateTradeSignal(self):
        print("generateTradeSignal")        
        self.trendCatchingFilterStocks(self)
        print("-------------------\n-------------")
        print('trendCatchingFilterStocks')
        print(self.tradeSignalData)
        

    def backTest(self):
        print("backTest")        

    def trendCatchingFilterStocks(self):
        '''
            Long pattern:
            1) Last 3-4 days correction (red candles)
            2) YD green candle
            3) Today gapdown open below YC/below YDH and above YD low and made no new low.
            4) BV after 15 minutes.
        '''
        mappingKeys = list(self.selectedStocksData)
        
        for stock in mappingKeys:
            #print('stockKey:', stock)
            data = self.selectedStocksData[stock]
            #(already sorted while insertion, last first)
            
            datalen = len(data)
            greencount = 0
            redcount = 0
            stockmove = []
            
            if(datalen>=4):
                dOP1 = float(data[0][2].replace(',',''))              
                dCP1 = float(data[0][5].replace(',',''))
                opcl1 = dCP1-dOP1
                if(opcl1 < 0):
                    stockmove.append('RED')
                    redcount = redcount+1
                else:
                    stockmove.append('GREEN')
                    greencount = greencount+1

                dOP2 = float(data[1][2].replace(',',''))
                dCP2 = float(data[1][5].replace(',',''))
                
                opcl2 = dCP2-dOP2
                if(opcl2 < 0):
                    stockmove.append('RED')
                    redcount = redcount+1
                else:
                    stockmove.append('GREEN')
                    greencount = greencount+1
                
                dOP3 = float(data[2][2].replace(',',''))
                dCP3 = float(data[2][5].replace(',',''))
               
                opcl3 = dCP3-dOP3
                if(opcl3 < 0):
                    stockmove.append('RED')
                    redcount = redcount+1
                else:
                    stockmove.append('GREEN')
                    greencount = greencount+1
                
                dOP4 = float(data[3][2].replace(',',''))
                dHP4 = float(data[3][3].replace(',',''))
                dLP4 = float(data[3][4].replace(',',''))
                dCP4 = float(data[3][5].replace(',',''))
                
                opcl4 = dCP4-dOP4
                if(opcl4 < 0):
                    stockmove.append('RED')
                    redcount = redcount+1
                else:
                    stockmove.append('GREEN')
                    greencount = greencount+1

                #print(data[4][1])
                todOP = float(data[4][1].replace(',',''))
                todHP = float(data[4][2].replace(',',''))
                todLP = float(data[4][3].replace(',',''))
                todCP = float(data[4][5].replace(',',''))
                
                todOpcl = todCP-todOP
                '''
                    short condn
                    prev 3D to YD upmove(green), YD Red, today OpenPP > YD-CP/YDLP (gapup coond)                    
                    short BV = HighPP > OpenPP and LTP < OpenPP 
                    so can short
                '''
                
                if(greencount >= 3 and stockmove[3] == 'RED'
                   and (todOP > dCP4 or todOP > dLP4)
                   and (todHP > todOP and todCP <= todOP)):
                    print(stock, " datalen::", datalen)
                    print(stockmove, greencount, redcount)
                    #short the stock
                    self.tradeSignalData[stock] = []
                    (self.tradeSignalData[stock]).append(['BOD: SHORT Below, SL', round(todOP,2), round(todHP,2), round(abs(todHP-todOP),2), 'GapUp-Bearish'])
                    
                '''
                    Long condn
                    prev 3D to YD downmove(red), YD green,
                    today OpenPP < YD-CP/YDHP (gapdown coond)                    
                    long BV = LowPP < OpenPP and LTP > OpenPP 
                    so can short
                '''
                if(redcount >= 3 and stockmove[3] == 'GREEN'
                   and (todOP < dCP4 or todOP < dHP4)
                   and (todLP < todOP and todCP >= todOP)):
                    print(stock, " datalen::", datalen)
                    print(stockmove, greencount, redcount)
                    #go long the stock
                    self.tradeSignalData[stock] = []
                    (self.tradeSignalData[stock]).append(['BOD: Long above, SL', round(todOP,2), round(todLP,2), round(abs(todLP-todOP),2), 'GapDown-Bullish'])    
               
               
                
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
        if(liveFileName!=''):        
            self.readLiveStocksDataFile(self, liveFileName, selectedStocksList, selectedStocksData)


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
            del lt[0]
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
 
