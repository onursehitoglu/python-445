%module quadtree   
%include "std_string.i"
%include "std_vector.i"
%{
#include "QuadTree.h"
%};

%include "QuadTree.h"
%template(LocationVector) std::vector<Location>;
