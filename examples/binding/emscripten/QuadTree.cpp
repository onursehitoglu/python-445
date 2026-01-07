#include <emscripten/emscripten.h>
#include <emscripten/bind.h>

using namespace emscripten;
#include "QuadTree.h"

// --- Rect Helper Methods ---

bool QuadTree::Rect::contains(double lat, double lon) const {
    return lat >= minLat && lat <= maxLat && lon >= minLon && lon <= maxLon;
}

bool QuadTree::Rect::intersects(const Rect& other) const {
    return !(other.minLat > maxLat || other.maxLat < minLat ||
             other.minLon > maxLon || other.maxLon < minLon);
}

// --- QuadTree Public Methods ---

QuadTree::QuadTree(double minLat, double minLon, double maxLat, double maxLon) 
    : boundary{minLat, minLon, maxLat, maxLon}, subdivided(false) {}

QuadTree::~QuadTree() = default;

void QuadTree::subdivide() {
    double midLat = (boundary.minLat + boundary.maxLat) / 2.0;
    double midLon = (boundary.minLon + boundary.maxLon) / 2.0;

    nw = std::make_unique<QuadTree>(midLat, boundary.minLon, boundary.maxLat, midLon);
    ne = std::make_unique<QuadTree>(midLat, midLon, boundary.maxLat, boundary.maxLon);
    sw = std::make_unique<QuadTree>(boundary.minLat, boundary.minLon, midLat, midLon);
    se = std::make_unique<QuadTree>(boundary.minLat, midLon, midLat, boundary.maxLon);

    subdivided = true;
}

bool QuadTree::insert(double lat, double lon, std::string text) {
	return insert(Location{lat, lon, text});
}


bool QuadTree::remove(double lat, double lon, std::string text) {
	return remove(Location{lat, lon, text});
}

bool QuadTree::insert(const Location& loc) {
    if (!boundary.contains(loc.lat, loc.lon)) return false;

    if (points.size() < CAPACITY && !subdivided) {
        points.push_back(loc);
        return true;
    }

    if (!subdivided) subdivide();

    if (nw->insert(loc)) return true;
    if (ne->insert(loc)) return true;
    if (sw->insert(loc)) return true;
    if (se->insert(loc)) return true;

    return false;
}

bool QuadTree::remove(const Location& loc) {
    if (!boundary.contains(loc.lat, loc.lon)) return false;

    for (auto it = points.begin(); it != points.end(); ++it) {
        if (it->lat == loc.lat && it->lon == loc.lon && it->title == loc.title) {
            points.erase(it);
            return true;
        }
    }

    if (subdivided) {
        if (nw->remove(loc)) return true;
        if (ne->remove(loc)) return true;
        if (sw->remove(loc)) return true;
        if (se->remove(loc)) return true;
    }
    return false;
}

std::vector<Location> QuadTree::query(double minLat, double minLon, double maxLat, double maxLon) const {
    std::vector<Location> found;
    Rect range{minLat, minLon, maxLat, maxLon};
    queryInternal(range, found);
    return found;
}

void QuadTree::queryInternal(const Rect& range, std::vector<Location>& found) const {
    if (!boundary.intersects(range)) return;

    for (const auto& p : points) {
        if (range.contains(p.lat, p.lon)) {
            found.push_back(p);
        }
    }

    if (subdivided) {
        nw->queryInternal(range, found);
        ne->queryInternal(range, found);
        sw->queryInternal(range, found);
        se->queryInternal(range, found);
    }
}

void QuadTree::clear(double minLat, double minLon, double maxLat, double maxLon) {
    Rect range{minLat, minLon, maxLat, maxLon};
    if (!boundary.intersects(range)) return;

    for (auto it = points.begin(); it != points.end(); ) {
        if (range.contains(it->lat, it->lon)) {
            it = points.erase(it);
        } else {
            ++it;
        }
    }

    if (subdivided) {
        nw->clear(minLat, minLon, maxLat, maxLon);
        ne->clear(minLat, minLon, maxLat, maxLon);
        sw->clear(minLat, minLon, maxLat, maxLon);
        se->clear(minLat, minLon, maxLat, maxLon);
    }
}


EMSCRIPTEN_BINDINGS(quadtree) {
	class_<Location>("Location")
	.property("lat",&Location::lat)
	.property("lon",&Location::lon)
	.property("title",&Location::title);
	class_<QuadTree>("QuadTree")
	.constructor<double,double,double,double>()
	.function("insert",select_overload<bool(double,double,std::string)>(&QuadTree::insert))
	.function("remove",select_overload<bool(double,double,std::string)>(&QuadTree::remove))
	.function("query", &QuadTree::query)
	.function("clear",&QuadTree::clear);
	register_vector<Location>("VecLocation");
}
