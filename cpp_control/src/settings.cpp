#include "settings.h"

#include <fstream>
#include <sstream>

static bool parseDouble(const std::string& s, double& out) {
	try {
		out = std::stod(s);
		return true;
	} catch (...) { return false; }
}

bool SettingsIO::loadFromJson(const std::string& path, ControlSettings& out) {
	std::ifstream in(path);
	if (!in.good()) return false;
	// Minimal JSON-like parser (expects lines: key: value)
	std::string line;
	while (std::getline(in, line)) {
		auto pos = line.find(':');
		if (pos == std::string::npos) continue;
		std::string key = line.substr(0, pos);
		std::string val = line.substr(pos + 1);
		// trim spaces
		key.erase(0, key.find_first_not_of(" \t\r\n"));
		key.erase(key.find_last_not_of(" \t\r\n") + 1);
		val.erase(0, val.find_first_not_of(" \t\r\n"));
		val.erase(val.find_last_not_of(" \t\r\n") + 1);
		if (key == "targetTorqueNm") parseDouble(val, out.targetTorqueNm);
		else if (key == "maxAngleDeg") parseDouble(val, out.maxAngleDeg);
		else if (key == "cycleHz") parseDouble(val, out.cycleHz);
	}
	return true;
}

bool SettingsIO::saveToJson(const std::string& path, const ControlSettings& cfg) {
	std::ofstream outF(path);
	if (!outF.good()) return false;
	outF << "targetTorqueNm: " << cfg.targetTorqueNm << "\n";
	outF << "maxAngleDeg: " << cfg.maxAngleDeg << "\n";
	outF << "cycleHz: " << cfg.cycleHz << "\n";
	return true;
}


