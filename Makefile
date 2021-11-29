# Trivial makefile for the calculator scanner/parser.
# Depends on default (built-in) rules for C compilation.

# Note that rule for goal (parse) must be the first one in this file.

parse: parse.o scan.o
	g++ -o parse parse.o scan.o

clean:
	rm *.o parse

test: parse
	./parse < ./tests/input.txt
test1: parse
	./parse < ./tests/input1.txt
test2: parse
	./parse < ./tests/input2.txt
test3: parse
	./parse < ./tests/input3.txt
test4: parse
	./parse < ./tests/input4.txt
test5: parse
	./parse < ./tests/input5.txt
test6: parse
	./parse < ./tests/input6.txt
test7: parse
	./parse < ./tests/input7.txt
test8: parse
	./parse < ./tests/input8.txt
test9: parse
	./parse < ./tests/input9.txt

parse.o: scan.h
scan.o: scan.h
