type ('terminal, 'nonterminal) symbol =
  | T of 'terminal
  | N of 'nonterminal

let convert_grammar gram1 = match gram1 with
(start, rules)-> let rec production nt prules = (match prules with 
                             |(stl, rule)::t->if stl = nt 
                                                  then rule::(production nt t)
                                                  else production nt t
                            |[]->[]
) in
(start, (fun nt -> production nt rules))
;;

let rec match_list productionf list symbol=match list with
|[]->false;;
|(T tterm)::tail->if tterm = symbol
                      then true 
                      else match_list productionf tail symbol
|(N nterm)::tail->match_table productionf (productionf nterm) symbol

and

rec match_table productionf rules symbol=match rules with
|[]->false;;
|head::tail->if match_list productionf head symbol
                  then true 
                  else match_table productionf tail symbol 
;;





let rec match_list 

let rec matcher productionf rules dev frag =match rules with
|head::tail->match head with 
                    |(N nterm)->matcher productionf (productionf nterm)
                    |(T tterm)->if List.hd(frag)=tterm
                                       then true
                                       else 

let parse_prefix gram acceptor frag =
  let matcher  (snd gram) ((snd gram) (fst gram))