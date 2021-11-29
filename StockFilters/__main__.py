import sys
sys.path.append(r"C:\Users\keyur\Documents\Keyur\TradeBook\PythonPrograms")

import TrendCatchingFilter as tcf
import VoltSquezFilter as vsf

def main():
    fInst = tcf.FileReader
    fInst.collectSelectedStocksData(fInst,
                                    'C:\\Users\\keyur\\Downloads\\MW-NIFTY-50-29-Nov-2021.csv',
                                    'C:\\Users\\keyur\\Downloads\\cm23NOV2021bhav.csv',
                                    'C:\\Users\\keyur\\Downloads\\cm24NOV2021bhav.csv',
                                    'C:\\Users\\keyur\\Downloads\\cm25NOV2021bhav.csv',
                                    'C:\\Users\\keyur\\Downloads\\cm26NOV2021bhav.csv',
                                    'C:\\Users\\keyur\\Downloads\\SelectedStocks.csv')
    sInst = tcf.StrategyBuilder; sInst.populate(sInst,fInst.selectedStocksData);
    sInst.generateTradeSignal(sInst);
    vInst = vsf.VoltSqzStrategyBuilder;
    vInst.populate(vInst, fInst.selectedStocksData, sInst.tradeSignalData);
    vInst.generateTradeSignal(vInst);


if __name__=="__main__":
    msg = main()
