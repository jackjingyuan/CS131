let convert_grammar gram1 = match gram1 with
(start, rules)-> let rec production nt prules = (match prules with 
                             |(stl, rule)::t->if stl = nt 
                                                  then rule::(production nt t)
                                                  else production nt t
                            |[]->[]
) in
(start, (fun nt -> production nt rules))