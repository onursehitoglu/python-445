# Python Binding with Swig Demo

## QuadTree

A QuadTree implementation in cpp is included in `QuadTree.h` and `QuadTree.cpp`.
Swig interface description is defined in `QuadTree.i`

## Build

 * Install swig and python development headers/libraries
 * run `swig -c++ -python QuadTree.i` to generate C++ wrapper and python file
 * run `g++ -fPIC -shared QuadTree.cpp QuadTree_wrap.cxx -o _quadtree.so` to
   compile the shared library file.
 * `import quadtree` in python will make the `QuadTree` and `Location` classes
   available in Python.

## Demo

`test.py` file is a demo of inserting, removing and querying entries in `QuadTree`
from Python
