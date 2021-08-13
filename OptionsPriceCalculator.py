import math, statistics, datetime
'''
Options Calculator
'''

class OptionPriceCalculator:

    int_rate = 0.1
    default_theta = 0.9
    year_d = 365
    
    
    def calcPrem(self, spot, strike, dayToExp, volt):
        
        print('calcPrem: spot', spot, 'strike', strike, 'dayToExp', dayToExp, 'volt', volt)
        #var d1 = (Math.log(spot/strike) + (int_rate + Math.pow(volt,2)/2) * delta_t) / (volt*Math.sqrt(delta_t)),
        
        volt = volt/100
        delta_t = 0.1
        if(dayToExp == 1):
            delta_t = self.default_theta/self.year_d
        else:
            delta_t = dayToExp/self.year_d
            
        d1 = (math.log(spot/strike) + (self.int_rate + (math.pow(volt,2))/2) * delta_t) / (volt*math.sqrt(delta_t))
        d1 = round(d1, 10)

        #var d2 = (Math.log(spot/strike) + (int_rate - Math.pow(volt,2)/2) * delta_t) / (volt*Math.sqrt(delta_t));
        d2 = (math.log(spot/strike) + (self.int_rate - math.pow(volt,2)/2) * delta_t) / (volt*math.sqrt(delta_t))
        d2 = round(d2, 10)
        print('delta_t', delta_t, 'd1', d1, 'd2', d2)
        Nd1 = round(self.cdf(d1), 10)
        Nd2 = round(self.cdf(d2), 10)
        print('Nd1', Nd1, 'Nd2', Nd2)
        _Nd1 = round(self.cdf(-1 * d1), 10)
        _Nd2 = round(self.cdf(-1 * d2), 10)
        print('_Nd1', _Nd1, '_Nd2', _Nd2)

        #var fv_strike = (strike)*Math.exp(-1*int_rate*delta_t);
        fv_strike = (strike) * math.exp (-1 * self.int_rate * delta_t)
        print('fv_strike', fv_strike)
        #var call_premium = spot * distribution.cdf(d1) - fv_strike * distribution.cdf(d2),
	#var put_premium = fv_strike * distribution.cdf(-1*d2) - spot * distribution.cdf(-1*d1);
        
        call_prem = spot * Nd1 - fv_strike * Nd2
        call_prem = round(call_prem, 2)
        put_prem = fv_strike * _Nd2 - spot * _Nd1
        put_prem = round(put_prem, 2)
        print('call_prem', call_prem, 'put_prem', put_prem)

        call_delta = Nd1
        call_delta = round(call_delta, 3)
        put_delta = Nd1 - 1
        put_delta = abs(round(put_delta, 3))

        #var call_gamma = distribution.pdf(d1)/(spot*volt*Math.sqrt(delta_t)), PDF
        PNd1 = round(self.pdf(d1), 10)
        print('PNd1', PNd1)
        call_gamma = PNd1 / (spot * volt * math.sqrt(delta_t))
        call_gamma = round(call_gamma, 4)
        put_gamma = call_gamma

        print('call_delta', call_delta, 'put_delta', put_delta, 'call_gamma', call_gamma)
        #use PDF (not CDF in Nd1) CSF = cumulative distribution, PDF is non-cumulative
        call_vega = (spot* PNd1 * math.sqrt(delta_t))/100
        call_vega = round(call_vega, 3)
        put_vega = call_vega
        print('call_vega', call_vega, 'put_vega', put_vega)
        
        #var call_theta = (-1*spot*distribution.pdf(d1)*volt/(2*Math.sqrt(delta_t)) - int_rate*fv_strike*distribution.cdf(d2))/365,
	#put_theta = (-1*spot*distribution.pdf(d1)*volt/(2*Math.sqrt(delta_t)) + int_rate*fv_strike*distribution.cdf(-1*d2))/365;
        call_theta = (-1*spot*Nd1*volt/(2*math.sqrt(delta_t)) - self.int_rate*fv_strike*Nd2)/self.year_d
        call_theta = round(call_theta, 3)
        put_theta = (-1*spot*Nd1*volt/(2*math.sqrt(delta_t)) + self.int_rate*fv_strike*_Nd2)/self.year_d
        put_theta = round(put_theta, 3)
        print('call_theta', call_theta, 'put_theta', put_theta)

    #cumulative normal distribution function 
    def cdf(x):
        # python doc calc
        #return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0 (python doc cunction)
        # zerodha js calulcator 
        #mean = 0, variance/stand Deviation = 1
        #0.5 * erfc(-(x - this.mean) / (this.standardDeviation * Math.sqrt(2)));
        val = 0.5 * math.erfc(- (x- 0) / (1 * math.sqrt(2)))
        return val

    #non-cumulative normal distribution function /probability density function
    def pdf(x):
        #zerodha js calulcator
        #mean = 0, variance/stand Deviation = 1
        #var m = this.standardDeviation * Math.sqrt(2 * Math.PI);
        #var e = Math.exp(-Math.pow(x - this.mean, 2) / (2 * this.variance));
        #return e / m;
        m_val = 1 * math.sqrt(2 * math.pi)
        e_val = math.exp(-math.pow(x - 0, 2) / (2 * 1))
        return e_val /m_val
