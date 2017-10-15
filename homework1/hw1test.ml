let my_subset_test0 = subset [] []
let my_subset_test1 = subset [3;1;3] [1;3;1]
let my_subset_test2 = not (subset [1;2] [])

let my_equal_sets_test0 = equal_sets [] []
let my_equal_sets_test1 = equal_sets [1;1;1] [1;1;1;1;1;1]
let my_equal_sets_test1 = not (equal_sets [] [1;2])

let my_set_union_test0 = equal_sets (set_union [1;2;3;4] []) [1;2;3;4]
let my_set_union_test1 = equal_sets (set_union [1;2;3;4] [3;1;3]) [1;2;3;4]
let my_set_union_test2 = equal_sets (set_union [1;1;1;1;1;1] []) [1;1]
let my_set_union_test3 = equal_sets (set_union [] [1;1;1;1;1;1]) [1]

let my_set_intersection_test0 =
  equal_sets (set_intersection [1;2;3;4;5] []) []
let my_set_intersection_test1 =
  equal_sets (set_intersection [1;2;3;5] [3;1;3]) [1;3]



let my_set_diff_test0 = equal_sets (set_diff [1;2;3;4;1] [1;4;3;5]) [2]
let my_set_diff_test1 = equal_sets (set_diff [] []) []

let my_computed_fixed_point_test0 =
  computed_fixed_point (=) (fun x -> sqrt x) 10000. = 1.

let my_computed_periodic_point_test0 =
  computed_periodic_point (=) (fun x -> -x) 2 (-1) = -1

let my_while_away_test0 = 
  equal_sets (while_away ((+) 3) ((>) 10) 0) [0; 3; 6; 9]
  
let my_rle_decode_test0 = 
  equal_sets (rle_decode [3,0; 1,6]) [0; 0; 0; 6]
let my_rle_decode_test1 = 
  equal_sets (rle_decode [3,"w"; 1,"x"; 0,"y"; 2,"z"]) ["w"; "w"; "w"; "x"; "z"; "z"]
let my_rle_decode_test2 =
  equal_sets (rle_decode [0, 2.0; 3, 0.0]) [0.0;0.0;0.0]

  type awksub_nonterminals =
    | Eggert | Smallberg | Nachenberg | Paul | Chen
  
  let awksub_rules =
     [Eggert, [T"("; N Eggert; T")"];
      Eggert, [N Chen];
      Eggert, [N Eggert; N Paul; N Eggert];
      Eggert, [N Smallberg];
      Eggert, [N Nachenberg; N Smallberg];
      Eggert, [N Smallberg; N Nachenberg];
      Smallberg, [T"$"; N Eggert];
      Nachenberg, [T"++"];
      Nachenberg, [T"--"];
      Paul, [T"+"];
      Paul, [T"-"];
      Chen, [T"0"];
      Chen, [T"1"];
      Chen, [T"2"];
      Chen, [T"3"];
      Chen, [T"4"];
      Chen, [T"5"];
      Chen, [T"6"];
      Chen, [T"7"];
      Chen, [T"8"];
      Chen, [T"9"]]

      let awksub_grammar = Expr, awksub_rules
      
      let my_filter_blind_alleys_test1 =
        filter_blind_alleys awksub_grammar = awksub_grammar
      
      let my_filter_blind_alleys_test1 =
        filter_blind_alleys (Expr, List.tl awksub_rules) = (Expr, List.tl awksub_rules)
      