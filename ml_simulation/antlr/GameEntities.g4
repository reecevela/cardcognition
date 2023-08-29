grammar GameEntities;

SELECTOR: 'a' | 'an' | 'the' | 'any' | 'each' | 'all' | 'target' | 'this' | 'cardname' ;




COUNTER: ( '+1/+1' | KEYWORD | '-1/-1' ) 'counter';

KEYWORD: 'flying' | 'vigilance' | 'wither' | 'first strike' | 'double strike' | 'deathtouch' | 'lifelink' | 'haste' | 'reach' | 'trample' | 'defender' | 'indestructible' | 'hexproof' | 'shroud' | 'intimidate' | 'exalted' | 'unblockable' | 'fear' | 'cascade';

PLAYER_POSSESSION: 'his' | 'her' | 'their' | 'its' | 'your' | PLAYER '\''? 's' ;
PLAYER: PLAYER_ATTRIBUTE player | 'you' | 'opponent' | 'player'; 
PLAYER_ATTRIBUTE: 'defending' | 'attacking'

CARD_TYPE: 'creature' | 'land' | 'artifact' | 'enchantment' | 'planeswalker' | 'instant' | 'sorcery';
ZONE: 'battlefield' | 'graveyard' | 'hand' | 'library' | 'exile' | 'stack' | 'command' | 'outside the game';

MANA_SYMBOL: '{' (NUMBER | [wW] | [uU] | [bB] | [rR] | [gG] | [sS] | [cC] | [pP] ) ( '/' (NUMBER | [wW] | [uU] | [bB] | [rR] | [gG] | [sS] | [cC] | [pP]))? '}';
RESOURCE_SYMBOL: '{' (e|t|q|s|m|x|y) '}' | MANA_SYMBOL;

REMINDER_TEXT: '(' .*? ')' -> channel(HIDDEN);