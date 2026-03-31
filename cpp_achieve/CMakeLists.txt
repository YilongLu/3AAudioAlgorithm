cmake_minimum_required(VERSION 3.16)
project(audio3a_cpp_skeleton LANGUAGES CXX)

add_library(audio3a_cpp
  src/pipeline_stub.cpp
  src/pipeline_c.cpp
)

target_include_directories(audio3a_cpp PUBLIC include)
target_compile_features(audio3a_cpp PUBLIC cxx_std_17)
