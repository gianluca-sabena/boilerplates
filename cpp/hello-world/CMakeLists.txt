cmake_minimum_required(VERSION 3.7)

if ( ${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR} )
    message( FATAL_ERROR "In-source builds not allowed. Please make a new directory (called a build directory) and run CMake from there. You may need to remove CMakeCache.txt." )
endif()

project(hello_world)

set(CMAKE_C_STANDARD 11)

set(SOURCE_FILES src/main/helloworld.cpp)
add_executable(hello_world ${SOURCE_FILES})
