#pragma once

#include <functional>
#include <string>

class TcpServer {
public:
	using CommandHandler = std::function<std::string(const std::string&)>;

	TcpServer() = default;
	bool start(unsigned short port, CommandHandler handler);
	void stop();

private:
	int serverFd{-1};
	bool running{false};
};


