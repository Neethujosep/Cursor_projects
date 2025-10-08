#include "measurement.h"

#include <cmath>

void SimpleMeasurement::reset() {
	timeSec = 0.0;
	torqueNm = 0.0;
	angleDeg = 0.0;
}

void SimpleMeasurement::step(double dtSec) {
	timeSec += dtSec;
	// Simulate torque rise and angle increase
	torqueNm = 6.0 * (1.0 - std::exp(-timeSec * 1.5));
	angleDeg += 30.0 * dtSec; // 30 deg/s
}


