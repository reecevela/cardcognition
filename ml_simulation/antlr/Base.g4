grammar Core;

NUMBER: [0-9]+;
NUMBER_WORDS: 'one' | 'two' | 'three' | 'four' | 'five' | 'six' | 'seven' | 'eight' | 'nine' | 'ten' | 'eleven' | 'twelve' | 'thirteen' | 'fourteen' | 'fifteen' | 'sixteen' | 'seventeen' | 'eighteen' | 'nineteen' | 'twenty' | 'thirty' | 'forty' | 'fifty' | 'sixty' | 'seventy' | 'eighty' | 'ninety' | 'one hundred';
COMMA: ',';
DOT: '.';
WS: [ \t\r\n]+ -> channel(HIDDEN);
NEWLINE: '\\n' ;
