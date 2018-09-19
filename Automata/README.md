# Algorithm of minimazing DFA
1. Run setup.sh
2. The "automata-minimization-1.0-jar-with-dependencies.jar" will be generated in the current directory
3. Run it via "java -jar automata-minimization-1.0-jar-with-dependencies.jar"
4. The program gets the path to the input file from stdin
5. Input file format:<br />
  i. The first line contains 4 integers: n -- number of states, s -- start state, f -- number of finish states, q -- alphabet size<br />
  ii. Next lines describes each state: a blank line and q lines in format "c i", where "c" is the character on the edge and "i" is the number of adjacent state. Characters may be enumerated in any order.<br />
  iii. The last line contains f integers -- numbers of finish states.<br />
(See examples in "tests" folder to learn more)
6. The program generates "output" folder, where you can find vizualized input and output automata and output.txt, describing the result in the same format.
