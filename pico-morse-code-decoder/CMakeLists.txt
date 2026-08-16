cmake_minimum_required(VERSION 3.13)

include("$ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake")
project(pico_morse_code_decoder C CXX ASM)

pico_sdk_init()

add_executable(pico_morse_decoder morse_code.c)
target_link_libraries(pico_morse_decoder pico_stdlib)
pico_add_extra_outputs(pico_morse_decoder)
