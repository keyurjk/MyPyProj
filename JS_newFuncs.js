    
	function testFunction() {
	  alert("You pressed a key inside the input field");
	}

    function getTimePart2() {
			time_str = curOHLCAry.time;
			//console.log('time_str:' + time_str);
			timeparts = time_str.split('T');
			timepart1 = timeparts[1]
			timepart2 = (timepart1.split('+'))[0]
			
			return timepart2;
	}
		
	function getTimePart1() {
		time_str = curOHLCAry.time;
		ltimepart1 = (time_str.split('+'))[0]
			
		return ltimepart1;
	}
		
	function createEntryTradeStr(action, timepart1, qty, entryPoint, strike, optionPP) {		
		curTradeStr = 'Entry |' + action + '| at [' + timepart1 + '] for qty [' + qty + '] & index [' + entryPoint + '], strike [' + strike + '], optionPP [' + optionPP + '];';
		console.log(curTradeStr);
	}
			
	function createExitTradeStr(action, pNl) {
		
		qty = document.getElementById('curQty').value	
		timepart1 = getTimePart1(); 
		exitPoint = curOHLCAry.close;
		strike = ''
		optionPP = ''
		
		if(action == 'Long') {
			strike = document.getElementById('c-strike').value;			 
			optionPP = document.getElementById('call-option-prem-value').value;
				
		} else if (action == 'Short') {
			strike = document.getElementById('p-strike').value;			 
			optionPP = document.getElementById('put-option-prem-value').value;
			
		}
		
		curTradeStr = 'Exit |' + action + '| at [' + timepart1 + '] for qty [' + qty + '] & index [' + exitPoint + '], strike [' + strike + '], optionPP [' + optionPP + '] and PNL:[' + pNl + '];';
		console.log(curTradeStr);
		//allTradesStr = allTradesStr + curTradeStr 	
	}		 