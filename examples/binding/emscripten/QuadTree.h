#ifndef QUADTREE_H
#define QUADTREE_H

#include <vector>
#include <string>
#include <memory>

struct Location {
    double lat;
    double lon;
    std::string title;
};

class QuadTree {
public:
    // Initial boundary: minLat, minLon, maxLat, maxLon
    QuadTree(double minLat, double minLon, double maxLat, double maxLon);
    ~QuadTree();

    // Insert a location
    bool insert(double, double, std::string);

    // Remove a specific location (matches coordinates and title)
    bool remove(double, double, std::string);

    // Query a rectangular region
    std::vector<Location> query(double minLat, double minLon, double maxLat, double maxLon) const;

    // Clear all values in a rectangular region
    void clear(double minLat, double minLon, double maxLat, double maxLon);

private:
    bool insert(const Location& loc);
    bool remove(const Location& loc);
    // Internal helper for range logic
    struct Rect {
        double minLat, minLon, maxLat, maxLon;
        bool contains(double lat, double lon) const;
        bool intersects(const Rect& other) const;
    };

    static const int CAPACITY = 4;
    Rect boundary;
    std::vector<Location> points;
    
    bool subdivided = false;
    std::unique_ptr<QuadTree> nw, ne, sw, se;

    // Internal recursive query
    void queryInternal(const Rect& range, std::vector<Location>& found) const;
    void subdivide();
};

#endif
