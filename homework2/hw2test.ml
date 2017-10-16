type ('nonterminal, 'terminal) symbol =
  | N of 'nonterminal
  | T of 'terminal

type awksub_nonterminals =
  | Expr | Lvalue | Incrop | Binop | Num

let awksub_rules =
   [Expr, [T"("; N Expr; T")"];
    Expr, [N Num];
    Expr, [N Expr; N Binop; N Expr];
    Expr, [N Lvalue];
    Expr, [N Incrop; N Lvalue];
    Expr, [N Lvalue; N Incrop];
    Lvalue, [T"$"; N Expr];
    Incrop, [T"++"];
    Incrop, [T"--"];
    Binop, [T"+"];
    Binop, [T"-"];
    Num, [T"0"];
    Num, [T"1"];
    Num, [T"2"];
    Num, [T"3"];
    Num, [T"4"];
    Num, [T"5"];
    Num, [T"6"];
    Num, [T"7"];
    Num, [T"8"];
    Num, [T"9"]]

let convert_grammar gram1 = match gram1 with
(start, rules)-> let rec production nt prules = (match prules with 
                             |(stl, rule)::t->if stl = nt 
                                                  then rule::(production nt t)
                                                  else production nt t
                            |[]->[]
) in
(start, (fun nt -> production nt rules))

let awksub_grammar = Expr, awksub_rules

let awksub_grammar_2=convert_grammar awksub_grammar