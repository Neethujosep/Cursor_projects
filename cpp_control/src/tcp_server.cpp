#include "tcp_server.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstring>
#include <thread>

bool TcpServer::start(unsigned short port, CommandHandler handler) {
	if (running) return true;
	serverFd = ::socket(AF_INET, SOCK_STREAM, 0);
	if (serverFd < 0) return false;

	int opt = 1;
	::setsockopt(serverFd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

	sockaddr_in addr{};
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = INADDR_ANY;
	addr.sin_port = htons(port);
	if (::bind(serverFd, (sockaddr*)&addr, sizeof(addr)) < 0) return false;
	if (::listen(serverFd, 1) < 0) return false;

	running = true;
	std::thread([this, handler]() {
		while (running) {
			sockaddr_in client{};
			socklen_t len = sizeof(client);
			int cfd = ::accept(serverFd, (sockaddr*)&client, &len);
			if (cfd < 0) continue;

			char buf[1024];
			ssize_t n = ::recv(cfd, buf, sizeof(buf)-1, 0);
			if (n > 0) {
				buf[n] = '\0';
				std::string req(buf);
				std::string resp = handler ? handler(req) : std::string("ERR:no_handler\n");
				::send(cfd, resp.c_str(), resp.size(), 0);
			}
			::close(cfd);
		}
	}).detach();
	return true;
}

void TcpServer::stop() {
	if (!running) return;
	running = false;
	if (serverFd >= 0) {
		::shutdown(serverFd, SHUT_RDWR);
		::close(serverFd);
		serverFd = -1;
	}
}


