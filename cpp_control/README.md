## Control Backend (C++17, CMake)

Implements a basic control loop for a screw/feeding/measuring system:
- Core loop with target torque and max angle cutoff
- Measurement simulator (torque/angle)
- Settings load/save (simple text format)
- TCP interface (START/STOP/STATUS) on port 9090
- Basic test target

### Build (Linux/macOS)
```bash
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
./control_tests
./control_daemon
```

### Build (Windows via Visual Studio)
```bash
mkdir build && cd build
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release
```

Run `control_daemon.exe` from the build folder.

### TCP usage
```bash
printf "START\n" | nc localhost 9090
printf "STATUS\n" | nc localhost 9090
printf "STOP\n" | nc localhost 9090
```


