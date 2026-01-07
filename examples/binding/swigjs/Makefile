CXXFLAGS=-fPIC -I/usr/include/node -I/usr/include/nodejs/src
LDFLAGS=$(shell pkg-config --libs python3)

all: build/Release/quadtree.node

QuadTree_wrap.cxx: QuadTree.i
	swig -c++ -javascript -node QuadTree.i

QuadTree.o: QuadTree.h QuadTree.cpp
	g++ $(CXXFLAGS) -c QuadTree.cpp

QuadTree_wrap.o: QuadTree_wrap.cxx
	g++ $(CXXFLAGS) -c $<

build/Release/quadtree.node: QuadTree.o QuadTree_wrap.o
	node-gyp rebuild

clean:
	-rm -rf QuadTree_wrap.cxx *.o build
