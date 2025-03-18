cmake_minimum_required(VERSION 3.14)

project(build VERSION 1.0 LANGUAGES CXX)

add_subdirectory(SIEdit/lib)

set(FLAG "$ENV{FLAG}")

add_executable(build
    build.cpp
)

target_compile_definitions(build
    PUBLIC FLAG="${FLAG}"
)

target_link_libraries(build 
    PUBLIC libweaver
)

target_include_directories(build
    PUBLIC SIEdit
)
