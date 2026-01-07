CXXFLAGS=-fPIC $(shell pkg-config --cflags python3)
LDFLAGS=$(shell pkg-config --libs python3)

all: _quadtree.so

QuadTree_wrap.cxx: QuadTree.i
	swig -c++ -python QuadTree.i

QuadTree.o: QuadTree.h QuadTree.cpp
	g++ $(CXXFLAGS) -c QuadTree.cpp

QuadTree_wrap.o: QuadTree_wrap.cxx
	g++ $(CXXFLAGS) -c $<

_quadtree.so: QuadTree.o QuadTree_wrap.o
	g++ -fPIC -shared QuadTree.o QuadTree_wrap.o -o $@ $(LDFLAGS)

clean:
	-rm *.o _quadtree.so QuadTree_wrap.cxx  quadtree.py quadtree.pyc
	-rm -rf __pycache__
