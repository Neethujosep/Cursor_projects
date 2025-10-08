#include "control_loop.h"

#include <chrono>
#include <cmath>

ControlLoop::ControlLoop(ControlSettings settings, MeasurementSource* measurement)
	: cfg(settings), meas(measurement) {}

ControlLoop::~ControlLoop() { stop(); }

void ControlLoop::setStatusCallback(StatusCallback cb) { statusCb = std::move(cb); }

void ControlLoop::start() {
	if (currentState == ControlState::Running) return;
	shouldRun = true;
	worker = std::thread(&ControlLoop::run, this);
}

void ControlLoop::stop() {
	shouldRun = false;
	if (worker.joinable()) worker.join();
	currentState = ControlState::Idle;
}

void ControlLoop::run() {
	using namespace std::chrono;
	const double dt = 1.0 / cfg.cycleHz;
	meas->reset();
	currentState = ControlState::Running;
	if (statusCb) statusCb("STATE:RUNNING");

	while (shouldRun) {
		const auto loopStart = steady_clock::now();
		meas->step(dt);
		double torque = meas->readTorqueNm();
		double angle = meas->readAngleDeg();

		if (statusCb) {
			statusCb("MEAS torque_nm=" + std::to_string(torque) + " angle_deg=" + std::to_string(angle));
		}

		if (torque >= cfg.targetTorqueNm || angle >= cfg.maxAngleDeg) {
			shouldRun = false;
		}

		const auto loopEnd = steady_clock::now();
		auto elapsed = duration_cast<microseconds>(loopEnd - loopStart).count();
		long sleepUs = static_cast<long>(std::max(0.0, dt * 1e6 - static_cast<double>(elapsed)));
		std::this_thread::sleep_for(microseconds(sleepUs));
	}

	currentState = ControlState::Idle;
	if (statusCb) statusCb("STATE:IDLE");
}


