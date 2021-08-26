from turtle import *


class Block(Turtle):
    
    def __init__(self, size):
        self.size = size
        Turtle.__init__(self, shape="square", visible=False)
        self.pu()
        self.shapesize(size * 1.5, 1.5, 2) # square-->rectangle
        if(size > 0):
            self.fillcolor("blue")            
        else:
            self.fillcolor("red")
        self.st()
    

    def glow(self):
        self.fillcolor("red")

    def unglow(self):
        self.fillcolor("black")

    def __repr__(self):
        return "Block size: {0}".format(self.size)


class Shelf(list):

    def __init__(self, y):
        "create a shelf. y is y-position of first block"
        self.y = y
        self.x = -150

    def push(self, d):
        width, _, _ = d.shapesize()
        # align blocks by the bottom edge
        y_offset = width / 2 * 20
        d.sety(self.y + y_offset)
        d.setx(self.x + 34 * len(self))
        d.write(d.size, align="center", font=("Courier", 16, "bold"))
        self.append(d)

    def _close_gap_from_i(self, i):
        for b in self[i:]:
            xpos, _ = b.pos()
            b.setx(xpos - 34)

    def _open_gap_from_i(self, i):
        for b in self[i:]:
            xpos, _ = b.pos()
            b.setx(xpos + 34)

    def pop(self, key):
        b = list.pop(self, key)
        b.glow()
        b.sety(200)
        self._close_gap_from_i(key)
        return b

    def insert(self, key, b):
        self._open_gap_from_i(key)
        list.insert(self, key, b)
        b.setx(self.x + 34 * key)
        width, _, _ = b.shapesize()
        # align blocks by the bottom edge
        y_offset = width / 2 * 20
        b.sety(self.y + y_offset)
        b.unglow()
    

def init_shelf():
    global s
    s = Shelf(-200)
    #values to show in bar 
    #  cumulative return, avg ret %, strike rate     
    s.push(Block(cum_ret))
    s.push(Block(strike_rate))
    s.push(Block(avg_ret_perc))

def show_text(text, line=0):
    line = 20 * line
    goto(0,150 - line)
    write(text, align="center", font=("Courier", 12))

def get_result_params():
    print()

def set_result_params(i_symbol, i_from_date_to_date, i_no_of_trades, i_strike_rate, i_avg_ret_perc, i_cum_ret):
    symbol = i_symbol
    from_date_to_date = i_from_date_to_date
    period = i_period
    no_of_trades = i_no_of_trades
    strike_rate = i_strike_rate
    avg_ret_perc = i_avg_ret_perc
    cum_ret = i_cum_ret
    cum_ret = cum_ret/100000 #in lacs
    
    
def main():
    getscreen().clearscreen()
    ht(); penup()
    init_shelf()
    tr_val = ['Trade Report for ' , symbol , ' for ' , period + ' from-to ' , from_date_to_date ,
    ' and count of trades: ' , str(no_of_trades)]
    tr_str = " ".join(tr_val)
    show_text(tr_str) #period(Yrs), from date to date, Symbol, no of trades,
    show_text(trade_strategy, line=2)
    show_text(exec_strategy, line=3)
    return "EVENTLOOP"

symbol = 'NA'
from_date_to_date = 'x to x'
period = 'x yrs'
no_of_trades = 10
strike_rate = -2
avg_ret_perc = 3
cum_ret = 0.4

trade_strategy = "Trade Strategy: Buy PE-CE ATM at ExpD at morning Open"
exec_strategy = "Execution Strategy: Buy two lots, exit 1st at 2.5 of opening PP and 2nd EOD."

if __name__=="__main__":
    msg = main()
    mainloop()
