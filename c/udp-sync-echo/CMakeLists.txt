cmake_minimum_required(VERSION 3.7)

if ( ${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR} )
    message( FATAL_ERROR "In-source builds not allowed. Please make a new directory (called a build directory) and run CMake from there. You may need to remove CMakeCache.txt." )
endif()

project(udp_sync_echo)

set(CMAKE_C_STANDARD 11)

set(SOURCE_FILES src/main.c)
add_executable(udp_sync_echo ${SOURCE_FILES})
add_executable(client src/client.c)
add_executable(server src/server.c)
add_executable(main src/main.c)
add_executable(pointers src/pointers.c)