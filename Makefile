# Makefile for Distance Vector Routing Assignment
# Creates executable files for both DistanceVector and PoisonedReverse

all: DistanceVector PoisonedReverse

DistanceVector: distance_vector.py
	copy distance_vector.py DistanceVector

PoisonedReverse: distance_vector.py
	copy poisoned_reverse.py PoisonedReverse

clean:
	if exist DistanceVector del DistanceVector
	if exist PoisonedReverse del PoisonedReverse

.PHONY: all clean