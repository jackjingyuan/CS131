type ('terminal, 'nonterminal) symbol =
  | T of 'terminal
  | N of 'nonterminal

type awksub_nonterminals =
  | Expr | Term | Lvalue | Incrop | Binop | Num

let grammar =
    (Expr,
     function
       | Expr ->
           [[N Term; N Binop; N Expr];
            [N Term]]
       | Term ->
     [[N Num];
      [N Lvalue];
      [N Incrop; N Lvalue];
      [N Lvalue; N Incrop];
      [T"("; N Expr; T")"]]
       | Lvalue ->
     [[T"$"; N Expr]]
       | Incrop ->
     [[T"++"];
      [T"--"]]
       | Binop ->
     [[T"+"];
      [T"-"]]
       | Num ->
     [[T"0"]; [T"1"]; [T"2"]; [T"3"]; [T"4"];
      [T"5"]; [T"6"]; [T"7"]; [T"8"]; [T"9"]])

let (nt, pfun)=grammar

let rec match_list productionf list symbol=match list with
  |[]->false
  |(T tterm)::tail->if tterm = symbol
                        then true 
                        else match_list productionf tail symbol
  |(N nterm)::tail->match_table productionf (productionf nterm) symbol
  
  and
  
match_table productionf rules symbol=match rules with
  |[]->false
  |head::tail->if match_list productionf head symbol
                    then true 
                    else match_table productionf tail symbol 
;;
match_table pfun (pfun nt) "++"                
  