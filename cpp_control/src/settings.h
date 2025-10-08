#pragma once

#include <string>

#include "control_loop.h"

namespace SettingsIO {
bool loadFromJson(const std::string& path, ControlSettings& out);
bool saveToJson(const std::string& path, const ControlSettings& cfg);
}


