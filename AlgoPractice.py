import csv, math, statistics, datetime, json, datetime, re

class AlgoPractice:

    def spiralOrder(self, A):
        result = []
        m = len(A)
        n = len(A[0])
        Tr = 0
        Br = m-1
        Lc = 0
        Rc = n-1
        dirn = 0

        while(Tr <= Br and Lc <= Rc):
                
            if(dirn == 0): #Right
                i = Lc
                while(i <= Rc):
                    result.append(A[Tr][i])
                    i = i + 1
                Tr = Tr +1
                dirn = 1
            elif(dirn == 1): #Down
                i = Tr
                while(i <= Br):
                    result.append(A[i][Rc])
                    i = i + 1
                Rc = Rc -1
                dirn = 2
            elif(dirn == 2): #Left
                i = Rc
                while(i >= Lc):
                    result.append(A[Br][i])
                    i = i -1
                Br = Br -1
                dirn = 3
            elif(dirn == 3): #Up
                i = Br
                while(i >= Tr):                    
                    result.append(A[i][Lc])
                    i = i - 1
                Lc = Lc +1
                dirn = 0
                
        return result

    def reverseSpiralOrder(self, A):
        print(A)
        result = []
        m = len(A)
        n = len(A[0])
        Tr = 0
        Br = m-1
        Lc = 0
        Rc = n-1
        dirn = 0
        while(Tr <= Br and Lc <= Rc):


            if(dirn == 0): #Down
                i = Tr
                while(i <= Br):
                    result.append(A[i][Lc])
                    i = i + 1
                Lc = Lc +1
                dirn = 1
            if(dirn == 1): #Right
                i = Lc
                while(i <= Rc):
                    result.append(A[Br][i])
                    i = i + 1
                Br = Br -1
                dirn = 2
            elif(dirn == 2): #Up
                i = Br
                while(i >= Tr):                    
                    result.append(A[i][Rc])
                    i = i - 1
                Rc = Rc -1
                dirn = 3
            elif(dirn == 3): #Left
                i = Rc
                while(i >= Lc):
                    result.append(A[Tr][i])
                    i = i -1
                Tr = Tr +1
                dirn = 0
            
                
        return result

    def monkeyDoorsProblem():
        doors = []
        monkeys = 100
        monkeynumber = 1
        opendoor = 1
        closedoor = 0
        i = 0
        while i <100:
            doors.append(1)
            i = i +1
        print('datalen', len(doors))    
        while monkeynumber < 100:
            
            monkeynumber = monkeynumber + 1
            startdoornumber = monkeynumber
            
            idx = startdoornumber-1
            touchdoorcount = 0
            while idx < 100:
                if(idx % monkeynumber == 0):
                    touchdoorcount = touchdoorcount + 1
                    if(doors[idx] == opendoor):
                        doors[idx] = closedoor
                    elif(doors[idx] == closedoor):
                        doors[idx] = opendoor
                idx = idx + 1

           
            print(idx, monkeynumber, startdoornumber, touchdoorcount, ':', doors.count(1))
        print(doors.count(1))        
                    
        
    def allFactors(self, A):
        
        
        if(A <= 1):
            return [A]
        factors = [1]
        lastfactors = []
        i = 2        
        rt = math.sqrt(A)
        while i <= rt:
            if(A%i == 0):
                factors.append(i)
                lastfactors.append(int(A/i))                
            i = i + 1

        if(rt%1 == 0):
            lastfactors.remove(rt)
        lastfactors.reverse()
        lastfactors.append(A)
        factors.extend(lastfactors)
        return factors

    def maxElemFinder(self, A):
        print(A)
        datalen = len(A)
        if(datalen <=2):
            return A[0]
        maxn = math.floor(datalen/2)
        i = 0
        loopcnt = maxn + 2
        elem = None
        retelem = None
        print(datalen, maxn, loopcnt)
        while i < loopcnt:
            elem = A[i]
            count = A.count(A[i])
            if (count > maxn):
                print(elem, count)
                retelem = elem
                break
            i = i + 1
        return retelem

    def distributeCandy(self, A):
        result = 0
        candies = []
        datalen = len(A)
        if(datalen == 1):
            if(A[0] > 1):
                return 2
            return 1
        
        i = 0

        '''
            approach
            1. find the least in the array, give 1 candy
            2. traverse left side, find the least and give 1 candy, 
        '''
        while(i < datalen):
            candies.append(1)
            i = i +1
        i  =1
        while(i < datalen-1):
        
            if(A[i] > A[i-1]):
                candies[i] = candies[i-1] + 1
                #print(1, A[i], candies[i])
                
            if(A[i] > A[i+1]):
                candies[i] = candies[i+1] + 1
                #print(2, A[i], candies[i])
            i = i + 1

            
        i  =datalen-2
        
        while(i > 0):
        
            if((A[i] > A[i-1]) and (candies[i] <= candies[i-1])):
                candies[i] = candies[i-1] + 1
                #print(3, A[i], candies[i])
            if((A[i] > A[i+1]) and (candies[i] <= candies[i+1])):
                candies[i] = candies[i+1] + 1
                #print(3, A[i], candies[i])
            i = i - 1
        
        if(A[0] > A[1]):
            candies[0] = candies[1] + 1

        if(A[datalen-1] > A[datalen-2]):
            candies[datalen-1] = candies[datalen-2] + 1
            
        i = 0
        #print(A)
        #print(candies)
        while (i < datalen):
            result = result + candies[i]
            i = i +1
        
        return result

    def binarySearch(self, A, tgt):
        minv = 0
        maxv = len(A)-1
        guess = -1
        midpoint = int((minv + maxv)/2)
        i = 0
        while(i <= int(maxv/2)):
            print(A[midpoint])
            if(tgt == A[midpoint]):
                print('iteration count', i)
                return tgt
            elif(tgt > A[midpoint]):
                minv = midpoint + 1
                midpoint = int((minv + maxv)/2)
            elif(tgt < A[midpoint]):
                maxv = midpoint -1
                midpoint = int((minv + maxv)/2)
            i = i + 1

        print('iteration count', i)
        return guess

    def swap(A, startIndex, endIndex):
        temp = A[startIndex]
        A[startIndex] = A[endIndex]
        A[endIndex] = temp

    def indexOfMinimumValue(A, startIndex):
        minValueIndex = startIndex
        minValue = A[startIndex]
        for i in range(startIndex+1, len(A)):
            if(A[i] < minValue):
                minValueIndex = i
                minValue = A[i]
        return minValueIndex
            
    def selectionSort(self, A):
        for i in range(0, len(A)):
            minValIndex = self.indexOfMinimumValue(A, i)
            if(minValIndex != i):
                self.swap(A, i, minValIndex)
            
        print(A)
    
def main():

    algoTest = AlgoPractice
     
    inputA = [ -939, 369, 319, 77, 128, -202, 282, 182, 83, -489, -443, -401, 385, 965, 0]
    print(inputA)            
    algoTest.selectionSort(algoTest, inputA)
    
    '''
    
    primesA = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    result = algoTest.binarySearch(algoTest, primesA, 43)
    print(result)

    #inputA = [ -255, 369, 319, 77, 128, -202, -147, 282, -26, -489, -443, -401, 385, 465, -134, 126, 304, 179, 16, 112, 473, -467, 279, -233, 66, 76, 408, 148, -369, 328, 138, -164, 492, -276, -326, 170, 168, 189, 13, 383, 341, 426, 219, 337, -62, -197, 263, 338, -324]

    inputA = [ 369, 369, 319, 77, 128, -202, 282, 282, 283, -489, -443, -401, 385, 465, 465]
                
    result = algoTest.distributeCandy(algoTest, inputA)
    
    inputA = [100, 1, 10]
    result = algoTest.maxElemFinder(algoTest, inputA)

    inputA = [
                [ 1, 2, 3, 4 ],
                [ 12, 13, 14, 5 ],
                [ 11, 16, 15, 6 ],
                [ 10, 9, 8, 7 ]
             ] 
    result = algoTest.reverseSpiralOrder(algoTest, inputA)
    '''
    #result = algoTest.allFactors(algoTest, 0)
    #print(result)
    #algoTest.monkeyDoorsProblem()
    #print(result)

    
if __name__=="__main__":
    msg = main()    
