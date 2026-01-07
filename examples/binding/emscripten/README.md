# Emscripten Demo

## QuadTree

A QuadTree implementation in cpp is included in `QuadTree.h` and `QuadTree.cpp`.
There is an emscripten/embind directive for defining class interface

## Build

 * Install emscripten compiler
 * run `em++ --bind QuadTree.cpp -o quadtree.js`

## Demo

There are two demo files:

  * `test.js` can be started from command line as `node test.js`
  * `test.html` upload a web server and start from browser. It is
    an interactive canvas with capital cities of the world inserted
    into quadtree and queried by selecting a region.
