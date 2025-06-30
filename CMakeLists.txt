cmake_minimum_required(VERSION 3.10)
project(CamSync)

set(CMAKE_CXX_STANDARD 17)

# Tell CMake where to find OpenSSL (adjust this if you installed somewhere else)
set(OPENSSL_ROOT_DIR "C:\Program Files\OpenSSL-Win64\bin\openssl.exe")

# Required so it finds OpenSSL::SSL and OpenSSL::Crypto targets
find_package(OpenSSL REQUIRED)

add_executable(CamSync CamSync.cpp)

# Include OpenSSL headers and link the libs
target_include_directories(CamSync PRIVATE ${OPENSSL_INCLUDE_DIR})
target_link_libraries(CamSync PRIVATE OpenSSL::SSL OpenSSL::Crypto)
