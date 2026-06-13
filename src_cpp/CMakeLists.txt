cmake_minimum_required(VERSION 3.10)
project(NCD_MST_Analysis)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Enable OpenMP for parallel computing
find_package(OpenMP REQUIRED)
find_package(ZLIB REQUIRED)

add_executable(ncd_mst_main main.cpp)
target_link_libraries(ncd_mst_main PRIVATE ZLIB::ZLIB OpenMP::OpenMP_CXX)
