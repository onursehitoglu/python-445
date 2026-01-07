# Javascript Binding with Swig Demo

## QuadTree

A QuadTree implementation in cpp is included in `QuadTree.h` and `QuadTree.cpp`.
Swig interface description is defined in `QuadTree.i`.
node-gyp build file is `binding.gyp`.

## Build

 * Install swig and node-gyp.
 * run `swig -c++ -javascript -node QuadTree.i` to generate C++ wrapper.
 * run `node-gyp rebuild` to create necessary files under `build/Release`
 * `require('build/Release/quadtree.node` in node will make the `QuadTree` and `LocationVector` classes
   available in node. `LocationVector` has `size()` and `get(index)` methods to access the query result.

## Demo

`test.js` file is a demo of inserting, removing and querying entries in `QuadTree`
from node.
