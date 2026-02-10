#include <math.h>

#define EARTH_RADIUS_KM 6371.0
#define PI 3.14159265358979323846

/**
 * Convert degrees to radians
 */
double deg_to_rad(double degrees) {
    return degrees * PI / 180.0;
}

/**
 * Calculate distance between two points using Haversine formula
 * Parameters:
 *   lat1, lon1: Coordinates of first point (in degrees)
 *   lat2, lon2: Coordinates of second point (in degrees)
 * Returns:
 *   Distance in kilometers
 */
double haversine_distance(double lat1, double lon1, double lat2, double lon2) {
    // Convert latitude and longitude from degrees to radians
    double lat1_rad = deg_to_rad(lat1);
    double lon1_rad = deg_to_rad(lon1);
    double lat2_rad = deg_to_rad(lat2);
    double lon2_rad = deg_to_rad(lon2);
    
    // Calculate differences
    double dlat = lat2_rad - lat1_rad;
    double dlon = lon2_rad - lon1_rad;
    
    // Haversine formula
    double a = sin(dlat / 2.0) * sin(dlat / 2.0) +
               cos(lat1_rad) * cos(lat2_rad) *
               sin(dlon / 2.0) * sin(dlon / 2.0);
    
    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));
    
    // Calculate distance
    double distance = EARTH_RADIUS_KM * c;
    
    return distance;
}
