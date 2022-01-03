import sys
sys.path.append(r"C:\Users\keyur\Documents\Keyur\TradeBook\PythonPrograms")

import NiftyAnalytics as nat

def main():
    nInst = nat.NiftyAnalytics
    nInst.long_max_exit_stddev = 30
    nInst.short_max_exit_stddev = 40
    nInst.readOHLCDataFile(nInst, 'C:\\Users\\keyur\\Documents\\Keyur\\TradeBook\\PythonPrograms\\NSE_Index_data.csv');

if __name__=="__main__":
    msg = main()
