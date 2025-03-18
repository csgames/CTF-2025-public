cmake_minimum_required(VERSION 3.14)

project(solve VERSION 1.0 LANGUAGES CXX)

add_subdirectory(SIEdit/lib)

add_executable(solve
    solve.cpp
)

target_link_libraries(solve 
    PUBLIC libweaver
)

target_include_directories(solve
    PUBLIC SIEdit
)
