add_library(control_backend
    control_loop.cpp
    control_loop.h
    settings.cpp
    settings.h
    tcp_server.cpp
    tcp_server.h
    measurement.cpp
    measurement.h
)

target_include_directories(control_backend PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(control_daemon main.cpp)
target_link_libraries(control_daemon PRIVATE control_backend)

