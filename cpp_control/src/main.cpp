#include <iostream>
#include <string>

#include "control_loop.h"
#include "measurement.h"
#include "settings.h"
#include "tcp_server.h"

int main(int argc, char** argv) {
	ControlSettings cfg;
	SettingsIO::loadFromJson("settings.txt", cfg);

	SimpleMeasurement meas;
	ControlLoop loop(cfg, &meas);
	loop.setStatusCallback([](const std::string& s){ std::cout << s << "\n"; });

	TcpServer server;
	server.start(9090, [&](const std::string& cmd){
		if (cmd.find("START") == 0) { loop.start(); return std::string("OK\n"); }
		if (cmd.find("STOP") == 0) { loop.stop(); return std::string("OK\n"); }
		if (cmd.find("STATUS") == 0) { return std::string("STATE?\n"); }
		return std::string("ERR:unknown\n");
	});

	std::cout << "Control daemon running on TCP 9090. Send START/STOP/STATUS. Ctrl+C to exit." << std::endl;
	while (true) { std::this_thread::sleep_for(std::chrono::seconds(1)); }
}


