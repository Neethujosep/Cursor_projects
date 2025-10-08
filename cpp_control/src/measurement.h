#pragma once

#include "control_loop.h"

class SimpleMeasurement : public MeasurementSource {
public:
	void reset() override;
	void step(double dtSec) override;
	double readTorqueNm() const override { return torqueNm; }
	double readAngleDeg() const override { return angleDeg; }
private:
	double timeSec{0.0};
	double torqueNm{0.0};
	double angleDeg{0.0};
};


