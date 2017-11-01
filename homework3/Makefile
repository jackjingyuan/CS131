JC=javac
JFlag=-g
JVM=java
TNum=32
JPack=jar
JPFlag=cf

all:
	$(JC) $(JFlag) BetterSafe.java GetNSet.java NullState.java State.java SwapTest.java SynchronizedState.java Unsynchronized.java UnsafeMemory.java
test:
		$(JVM) UnsafeMemory Synchronized $(TNum) 1000000 6 5 6 3 0 3
		$(JVM) UnsafeMemory GetNSet $(TNum) 1000000 6 5 6 3 0 3
		$(JVM) UnsafeMemory BetterSafe $(TNum) 1000000 6 5 6 3 0 3
BetterSafe:
	$(JVM) UnsafeMemory BetterSafe $(TNum) 1000000 6 5 6 3 0 3

GetNSet:
	$(JVM) UnsafeMemory GetNSet $(TNum) 1000000 6 5 6 3 0 3

Synchronized:
	$(JVM) UnsafeMemory Synchronized $(TNum) 1000000 6 5 6 3 0 3

Unsynchronized:
	$(JVM) UnsafeMemory Unsynchronized $(TNum) 1000000 6 5 6 3 0 3

Null:
	$(JVM) UnsafeMemory Null $(TNum) 1000000 6 5 6 3 0 3
Jar:
	$(JPack) $(JPFlag) jmmplus.jar BetterSafe.java GetNSet.java NullState.java State.java SwapTest.java SynchronizedState.java Unsynchronized.java UnsafeMemory.java
clean:
	rm -f *.class