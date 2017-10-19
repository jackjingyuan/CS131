type ('terminal, 'nonterminal) symbol =
  | T of 'terminal
  | N of 'nonterminal

  type awksub_nonterminals =
    | Eggert | Smallberg | Nachenberg | Paul | Chen |Haocong

    let accept_all derivation string = Some (derivation, string)
    let accept_empty_suffix derivation = function
       | [] -> Some (derivation, [])
       | _ -> None
    
    let test_grammar_0 = (Eggert,
      function
        | Eggert ->
            [[N Smallberg ; N Chen; N Eggert];
             [N Smallberg ]]
        | Smallberg  ->
      [[N Haocong];
       [N Nachenberg];
       [N Paul; N Nachenberg];
       [N Nachenberg; N Paul];
       [T"("; N Eggert; T")"]]
        | Nachenberg ->
      [[T"$"; N Eggert]]
        | Paul ->
      [[T"++"];
       [T"--"]]
        | Chen ->
      [[T"+"];
       [T"-"]]
        | Haocong ->
      [[T"0"]; [T"1"]; [T"2"]; [T"3"]; [T"4"];
       [T"5"]; [T"6"]; [T"7"]; [T"8"]; [T"9"]])

       let rec match_rule productionf rule acceptor derv fram =match rule with
       |[]->acceptor derv fram
       |hd::tl->match fram with
                    |[]->None
                    |hsymbol::tsymbol->match rule with 
                                       |(T tterm)::tail->if tterm = hsymbol
                                                                  then match_rule productionf tail acceptor derv tsymbol
                                                                  else None
                                      |(N nterm)::tail->(match_table productionf (productionf nterm) nterm (match_rule productionf tail acceptor) derv fram)
                                      
       and 
       match_table productionf rules nonterm acceptor derv fram = match rules with 
       |[]->None
       |hd::tl->match (match_rule productionf hd acceptor (derv@[nonterm, hd]) fram) with 
                |None->match_table productionf tl nonterm acceptor derv fram
                |x-> x              
       
       
       
       let parse_prefix gram acceptor frag = match gram with
       |(nonterm, productionf)->match_table productionf (productionf nonterm) nonterm acceptor [] frag


       
       let test1 =
        ((parse_prefix test_grammar_0 accept_all ["9"])
         = Some ([(Eggert, [N Smallberg ]); (Smallberg , [N Haocong]); (Haocong, [T "9"])], []))
      
      let test2 =
        ((parse_prefix test_grammar_0 accept_all ["9"; "+"; "$"; "1"; "+"])
         = Some
             ([(Eggert, [N Smallberg ; N Chen; N Eggert]); (Smallberg , [N Haocong]); (Haocong, [T "9"]);
         (Chen, [T "+"]); (Eggert, [N Smallberg ]); (Smallberg , [N Nachenberg]);
         (Nachenberg, [T "$"; N Eggert]); (Eggert, [N Smallberg ]); (Smallberg , [N Haocong]);
         (Haocong, [T "1"])],
        ["+"]))
