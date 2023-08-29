grammar MTG;

// Parser Rules

root: ability_clause+ ;

ability_clause: ability NEWLINE? ;

ability: keywordList | triggeredAbility | activatedAbility | spellAbility | staticAbility ;

keywordList: KEYWORD (',' KEYWORD)* ;

triggeredAbility: TRIGGER triggerCondition ',' effect DOT ;

spellAbility: (SUBACTION selector gameEntity | action) DOT ;

activatedAbility: activationCost ':' effect '.' ;

triggerCondition: gameEntity eventOrContext ;

gameEntity: selector? STATUS? (CARD_TYPE 's'? 'es'? | COUNTER 'counter' 's'? | 'card' | 'life' | 'mana' | 'damage' | 'turn' | 'step' | 'phase' | PLAYER) ;

effect: (selector? PLAYER)? 'may'? ( action | gameEntity action ) ;

controlCondition: 'under' selector 'control' ;

contextCondition: 'as long as' condition;

condition: PLAYER ('control' | 'controls') count? gameEntity 's'? ;

eventOrContext: event | contextCondition ;

// Actions and effects

SUBACTION: 'attack' 
         | 'block' 
         | 'draw' 
         | 'gain' 
         | 'lose' 
         | 'put'
         | 'create'
         | 'destroy'
         //| 'exile'
         | 'return'
         | 'sacrifice'
         | 'shuffle'
         | 'tap'
         | 'untap'
         | 'equip'
         | 'attach'
         | 'detach'
         | 'transform'
         | 'counter'
         | 'bounce'
         | 'mill'
         | 'burn'
         | 'clone'
         | 'discard'
         | 'search'
         | 'scry'
         | 'reveal'
         | 'set'
         | 'play'
         | 'cast'
         | 'regenerate'
         | 'control'
         | 'activate'
         | 'deactivate'
         | 'flip'
         | 'phase'
         | 'fateseal'
         | 'suspend'
         | 'cycle'
         | 'add'
         | 'remove'
         | 'rearrange'
         | 'replace'
         | 'switch'
         | 'prevent'
         | 'redirect'
         | 'choose'
         | 'copy'
         | 'double'
         | 'halve'
         | 'multiply'
         | 'flicker'
         | 'manifest'
         | 'prowess'
         | 'embalm'
         | 'eternalize'
         | 'exert'
         | 'explore'
         | 'adapt'
         | 'amass'
         | 'bolster'
         | 'devour'
         | 'fabricate'
         | 'investigate'
         | 'populate'
         | 'proliferate'
         | 'support'
         | 'meld'
         | 'increase'
         | 'decrease'
        // | 'transform'
         | 'cost'
         | 'fight'
         | 'become'
         | 'enters'
         | 'leaves'
         | 'win'
       //  | 'lose'
        // | 'end'
         | 'end'
         | 'exchange'
         | 'gain control of'
        // | 'have'
         | 'are'
         | 'is'
         | 'move'
         | 'pair'
         | 'be'
         | 'come'
         | 'skip'
         | 'take'
         | 'kick'
         | 'share'
         //| 'get'
         ;

action: 'deals' count 'damage' 
    | 'becomes' 
    | 'attacks' 
    | 'blocks' 
    | 'draws' count 'cards'
    | 'loses' count 'life'
    | 'gains' count 'life'
    | 'puts' count COUNTER 's'? 'on' selector gameEntity (PLAYER 'control' 's'?)?
    | 'removes' count COUNTER 's'? 'from' selector gameEntity (PLAYER 'control' 's'?)?
    | 'looks' 'at' count 'cards' 'of' PLAYER_POSSESSION 'library'
    | 'puts' count 'cards of' PLAYER_POSSESSION 'library' 'into' PLAYER_POSSESSION 'graveyard'
    ;

selfAction: 'gain' count 'life'
    | 'gain life' count
    | 'lose' count 'life'
    | 'lose life' count
    | 'draw' count 'cards'
    | 'draw cards' count
    | 'discard' count 'cards'
    | 'discard cards' count
    | 'look at the top' count 'cards of' selector? PLAYER_POSSESSION 'library'
    | 'scry' count
    | 'put' count 'cards of' PLAYER_POSSESSION 'library' 'into' PLAYER_POSSESSION 'graveyard'
    | 'shuffle' selector? PLAYER_POSSESSION 'library'
    | 'put' selector gameEntity 'into' selector? count ZONE
    | 'sacrifice' selector gameEntity
    | 'destroy' selector gameEntity
    | 'exile' selector gameEntity
    | 'return' selector gameEntity 'to' selector? ZONE
    ;

event: ('enters' | 'leaves') selector ZONE controlCondition? ;

/// counting

count: count 'or more' | count 'or less' | NUMBER | NUMBER_WORD | 'up to' count | 'any number of' count | 'a' | 'equal to' count | 'the number of' gameEntity 's' PLAYER 'control' 's'? |  'the top' count | 'the bottom' count;

activationCost: (MANA_SYMBOL | NUMBER | NUMBER_WORD) (',' (MANA_SYMBOL | NUMBER | NUMBER_WORD) )* ;

staticAbility: gameEntity 's'? POSSESS '"' ability '"' '.' ;

// Lexer Rules
MANA_SYMBOL: '{' (NUMBER | [wW] | [uU] | [bB] | [rR] | [gG] | [sS] | [cC] | [pP] ) ( '/' (NUMBER | [wW] | [uU] | [bB] | [rR] | [gG] | [sS] | [cC] | [pP]))? '}';
RESOURCE_SYMBOL: '{' ('e'|'t'|'q'|'s'|'m'|'x'|'y') '}' | MANA_SYMBOL;
ZONE: 'battlefield' | 'graveyard' | 'hand' | 'library' | 'exile' | 'stack' | 'command' | 'outside the game';

TRIGGER: 'whenever' | 'when' | 'at';
COUNTER: ( '+1/+1' | KEYWORD | '-1/-1' ) 'counter';

selector: 'a' | 'an' | 'the' | 'any' | 'each' | 'all' | 'target' | 'this' | 'cardname' | 'its' | 'with' ATTRIBUTE count ;

POSSESS: 'have' | 'get' ;
PLAYER_POSSESSION: 'his' | 'her' | 'their' | 'your' | PLAYER '\''? 's' ;
PLAYER: STATUS PLAYER | 'you' | 'opponent' | 'player'; 

CARD_TYPE: 'creature' | 'land' | 'artifact' | 'enchantment' | 'planeswalker' | 'instant' | 'sorcery';
STATUS: 'un'? 'tapped' | 'equipped' | 'attacking' | 'blocking' | 'enchanted' ;
ATTRIBUTE: 'non'? 'token' | 'power' | 'toughness' | 'mana value' | 'converted mana cost' | COLOR;
KEYWORD: 'flying' | 'vigilance' | 'wither' | 'first strike' | 'double strike' | 'deathtouch' | 'lifelink' | 'haste' | 'reach' | 'trample' | 'defender' | 'indestructible' | 'hexproof' | 'shroud' | 'intimidate' | 'exalted' | 'unblockable' | 'fear' | 'cascade';

COLOR: 'white' | 'blue' | 'black' | 'red' | 'green' | 'colorless';

NUMBER: [0-9]+;
NUMBER_WORD: 'one' | 'two' | 'three' | 'four' | 'five' | 'six' | 'seven' | 'eight' | 'nine' | 'ten' | 'eleven' | 'twelve' | 'thirteen' | 'fourteen' | 'fifteen' | 'sixteen' | 'seventeen' | 'eighteen' | 'nineteen' | 'twenty' | 'thirty' | 'forty' | 'fifty' | 'sixty' | 'seventy' | 'eighty' | 'ninety' | 'one hundred';
COMMA: ',';
DOT: '.';
WS: [ \t\r\n]+ -> channel(HIDDEN);

NEWLINE: '\n' ;
REMINDER_TEXT: '(' .*? ')' -> channel(HIDDEN);