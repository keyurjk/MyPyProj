import sys
sys.path.append(r"C:\Users\keyur\Documents\Keyur\TradeBook\PythonPrograms")

import TrendCatchingFilter as tcf
import VoltSquezFilter as vsf
import BackTester as bts

def main():
    fInst = tcf.FileReader
    fInst.collectSelectedStocksData(fInst,
                                    'C:\\Users\\keyur\\Downloads\\MW-NIFTY-50-09-Dec-2021.csv',
                                    'C:\\Users\\keyur\\Downloads\\cm03DEC2021bhav.csv',                            
                                    'C:\\Users\\keyur\\Downloads\\cm06DEC2021bhav.csv',
                                    'C:\\Users\\keyur\\Downloads\\cm07DEC2021bhav.csv',
                                    'C:\\Users\\keyur\\Downloads\\cm08DEC2021bhav.csv',        
                                    'C:\\Users\\keyur\\Downloads\\SelectedStocks.csv')
    sInst = tcf.StrategyBuilder; sInst.populate(sInst, fInst.selectedStocksData);
    sInst.morngBODFilter=1;
    sInst.generateTradeSignal(sInst);
    '''
    
    vInst = vsf.VoltSqzStrategyBuilder;
    vInst.populate(vInst, fInst.selectedStocksData, sInst.tradeSignalData);
    vInst.generateTradeSignal(vInst);
    '''

    btsInst = bts.BackTester
    
    fInst.readLiveStocksDataFile(fInst,
                                 'C:\\Users\\keyur\\Downloads\\Post-NIFTY-50-09-Dec-2021.csv',
                                 fInst.selectedStocksList,
                                 btsInst.closeOfDayData)
    btsInst.populate(btsInst, sInst.tradeSignalData)
    btsInst.runBackTestForTrendCatchFilter(btsInst)
    

    
    
if __name__=="__main__":
    msg = main()
