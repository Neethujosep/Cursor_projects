#pragma once

#include <atomic>
#include <functional>
#include <mutex>
#include <thread>
#include <vector>

enum class ControlState { Idle, Running, Error };

struct ControlSettings {
	// core settings
	double targetTorqueNm{5.0};
	double maxAngleDeg{360.0};
	double cycleHz{200.0};
};

class MeasurementSource {
public:
	virtual ~MeasurementSource() = default;
	virtual void reset() = 0;
	virtual void step(double dtSec) = 0;
	virtual double readTorqueNm() const = 0;
	virtual double readAngleDeg() const = 0;
};

class ControlLoop {
public:
	using StatusCallback = std::function<void(const std::string&)>;

	explicit ControlLoop(ControlSettings settings, MeasurementSource* measurement);
	~ControlLoop();

	void start();
	void stop();
	void setStatusCallback(StatusCallback cb);
	ControlState state() const { return currentState; }

private:
	void run();

	ControlSettings cfg;
	MeasurementSource* meas;
	std::atomic<ControlState> currentState{ControlState::Idle};
	std::atomic<bool> shouldRun{false};
	std::thread worker;
	StatusCallback statusCb;
	mutable std::mutex mtx;
};


