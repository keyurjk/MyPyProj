import csv, statistics, datetime, re
#import os, urllib.request, concurrent.futures  
'''
version1: BackTest trendcatching filter.
version1.1: 

'''


    
'''
----------------
'''
class BackTester:

    tradeSignalData=''
    closeOfDayData=dict()

    def populate(self, itradeSignalData):
        print("populate")
        self.tradeSignalData=''
        self.tradeSignalData = itradeSignalData
        
    def runBackTestForTrendCatchFilter(self):

        '''
        1. Loop thru trade signal data
        2. Get each stock and its move predcn
        3. Get the same stock data from closeOfDayData
        4. Test if SL hit, if new high/low was made
        Else diff of EOD PP -Entry PP and see how much made against predfn SL. (R:R)        
        '''
        mappingKeys = list(self.tradeSignalData)
        slCount = 0
        allCount = len(mappingKeys)
        totalPnL = 0
        totalRR = 0
        avgRR = 0
        for stock in mappingKeys:
            signalData = self.tradeSignalData[stock]
            #print('BackTest:', stock)
            signal = signalData[0][0]
            entryPP = float(signalData[0][1])
            slPP = float(signalData[0][2])
            slDiff = float(signalData[0][3])
            
            
            print(stock, signal, entryPP, slPP, slDiff)

            data = self.closeOfDayData[stock]
            todOP = float(data[0][1].replace(',',''))
            todHP = float(data[0][2].replace(',',''))
            todLP = float(data[0][3].replace(',',''))
            todCP = float(data[0][5].replace(',',''))
            
            print(stock, todOP, todHP, todLP, todCP)
            
            if(re.search('Long',signal)):
                if(todLP<slPP):
                    print(stock, 'Long: SL hit')
                    slCount = slCount + 1
                else:
                    pnlDiff = todCP - (entryPP+slDiff)
                    totalPnL = totalPnL + pnlDiff
                    rr = min(round(pnlDiff/slDiff,1),10)
                    totalRR = totalRR + rr
                    #print(stock, 'PnL', round(pnlDiff, 2), 'R:R 1:', rr)

            if(re.search('SHORT',signal)):
                if(todHP>slPP):
                    print(stock, 'Short: SL hit')
                    slCount = slCount + 1
                else:
                    pnlDiff = (entryPP-slDiff) - todCP
                    totalPnL = totalPnL + pnlDiff
                    rr = min(round(pnlDiff/slDiff,1),10)
                    totalRR = totalRR + rr
                    #print(stock, 'PnL', round(pnlDiff, 2), 'R:R 1:',rr)
        avgRR = round(totalRR/allCount,2)
        
        print('Allcount', allCount,'slCount:', slCount, 'Total PnL', round(totalPnL,2), 'avg R:R', avgRR)                 
        

