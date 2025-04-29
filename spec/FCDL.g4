
// ver 1.1 (c) S*elf Apr 22,2025
//
// ─────────────────────────── HEADER ───────────────────────────
grammar FCDL;

// ─────────────────────────── LEXER  (UPPER-CASE) ──────────────
DECIMAL : [0-9]+ '.' [0-9]+ ;
STRING  : '"' ( ~["\r\n] )* '"' ;
VERSION : [0-9]+ '.' [0-9]+ ;
ID : [A-Za-z_][A-Za-z_0-9.]* ;
NUMBER  : [0-9]+ ;
WS      : [ \t\r\n]+ -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;

// ─────────────────────────── PARSER  (lower-case) ─────────────
file            : systemDecl EOF ;

systemDecl
    : 'system' STRING ('version' '=' VERSION)?
      attrList?
      '{' systemBody '}'
    ;

systemBody
    : moduleDecl* orchestrationDecl            // orchestrator mandatory 
    ;

moduleDecl
    : 'module' STRING attrList?              // module name + optional attrs
      '{'
           'type' '=' ID attrList?           // mandatory line inside braces
           layerDecl*                        // 0-N layers
      '}'
    ;

layerDecl
    : 'layer' attrList
    ;

orchestrationDecl
    : 'orchestration' attrList? '{' attrList '}'    // inner attrList now mandatory
    ;

orchestrationBody
    : attrList?
    ;

attrList
    : '(' (attrPair (',' attrPair)*)? ')'
    ;

attrKey   
    : ID 
    | 'type' 
    | 'layer' 
    | 'tool' 
    | 'deployment' 
    | 'strategy' 
    ;

attrPair
    : attrKey '=' value
    ;

value
    : STRING
    | DECIMAL
    | NUMBER
    | ID
    ;
