cmake_minimum_required(VERSION 3.13)

include("$ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake")
project(week06 C CXX ASM)

pico_sdk_init()

add_executable(out morse_code.c)
target_link_libraries(out pico_stdlib)

