#include "control_loop.h"
#include "measurement.h"

#include <cassert>

int main() {
	ControlSettings cfg; cfg.targetTorqueNm = 1.0; cfg.maxAngleDeg = 45.0; cfg.cycleHz = 100.0;
	SimpleMeasurement meas;
	ControlLoop loop(cfg, &meas);
	loop.start();
	std::this_thread::sleep_for(std::chrono::milliseconds(200));
	loop.stop();
	assert(loop.state() == ControlState::Idle);
	return 0;
}


