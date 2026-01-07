var qt = require("./build/Release/quadtree.node")

capitals = [[35.6895, 139.6917, "Tokyo"], [48.8566, 2.3522, "Paris"], [38.8951, -77.0364, "Washington D.C."],
	[51.5074, -0.1278, "London"], [-35.2809, 149.1300, "Canberra"], [55.7558, 37.6173, "Moscow"],
	[39.9042, 116.4074, "Beijing"], [-15.7975, -47.8919, "Brasilia"], [30.0444, 31.2357, "Cairo"],
	[52.5200, 13.4050, "Berlin"], [28.6139, 77.2090, "New Delhi"], [-34.6037, -58.3816, "Buenos Aires"],
	[41.9028, 12.4964, "Rome"], [59.3293, 18.0686, "Stockholm"], [45.4215, -75.6972, "Ottawa"],
	[34.0209, -6.8416, "Rabat"], [1.3521, 103.8198, "Singapore"], [-1.2921, 36.8219, "Nairobi"],
	[40.4168, -3.7038, "Madrid"], [59.9139, 10.7522, "Oslo"], [19.4326, -99.1332, "Mexico City"],
	[33.3152, 44.3661, "Baghdad"], [-33.9249, 18.4241, "Cape Town"], [52.2297, 21.0122, "Warsaw"],
	[23.6850, 90.3563, "Dhaka"], [-6.2088, 106.8456, "Jakarta"], [35.6892, 51.3890, "Tehran"],
	[33.6844, 73.0479, "Islamabad"], [52.3676, 4.9041, "Amsterdam"], [50.8503, 4.3517, "Brussels"],
	[47.3769, 8.5417, "Zurich"], [37.5665, 126.9780, "Seoul"], [21.0285, 105.8542, "Hanoi"],
	[13.7563, 100.5018, "Bangkok"], [6.9271, 79.8612, "Colombo"], [44.4268, 26.1025, "Bucharest"],
	[47.4979, 19.0402, "Budapest"], [50.0755, 14.4378, "Prague"], [59.4370, 24.7535, "Tallinn"],
	[56.9496, 24.1052, "Riga"], [54.6872, 25.2797, "Vilnius"], [60.1695, 24.9354, "Helsinki"],
	[55.6761, 12.5683, "Copenhagen"], [37.9838, 23.7275, "Athens"], [39.9334, 32.8597, "Ankara"],
	[31.7683, 35.2137, "Jerusalem"], [33.8938, 35.5018, "Beirut"], [24.7136, 46.6753, "Riyadh"],
	[25.2048, 55.2708, "Abu Dhabi"], [3.1390, 101.6869, "Kuala Lumpur"]
]

capmap = new qt.QuadTree(-180,-180, 180,180)

for (v of capitals) {
	capmap.insert(v[0], v[1], v[2])
}

console.log("ALL ------------")

var qr =  capmap.query(0,0,50,50)

for (var i = 0; i < qr.size(); i++) {
	var loc = qr.get(i)
	console.log(loc.lat, loc.lon, loc.title)
}

console.log("MID ------------")
qr =  capmap.query(20,20,40,40)

for (var i = 0; i < qr.size(); i++) {
	var loc = qr.get(i)
	console.log(loc.lat, loc.lon, loc.title)
}

capmap.clear(0,0,35,50)

console.log("REM ------------")
qr =  capmap.query(0,0,50,50)

for (var i = 0; i < qr.size(); i++) {
	var loc = qr.get(i)
	console.log(loc.lat, loc.lon, loc.title)
}
