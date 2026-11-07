cmake_minimum_required(VERSION 3.5)

install(DIRECTORY ${PROJECT_SOURCE_DIR}/python/mpc_fatigue/
        DESTINATION ${CATKIN_PACKAGE_PYTHON_DESTINATION}
        FILES_MATCHING PATTERN "*.py")

option(BUILD_LEGACY_CPP_CASADI_BINDING "Build the C++ CasADi bridge" OFF)

if(BUILD_LEGACY_CPP_CASADI_BINDING)
    set(PYBIND11_PYTHON_VERSION 2.7)
    find_package(pybind11 REQUIRED)

    message(STATUS "Compiling python bindings")
    include_directories(${CMAKE_CURRENT_SOURCE_DIR})

    find_package(urdfdom REQUIRED)
    find_package(Boost REQUIRED COMPONENTS system)
    find_package(casadi REQUIRED)

    pybind11_add_module(pynocchio_casadi pynocchio_casadi.cpp)
    target_link_libraries(pynocchio_casadi PUBLIC
        ${CASADI_LIBRARIES}
        ${urdfdom_LIBRARIES}
        ${Boost_LIBRARIES})

    install(TARGETS pynocchio_casadi
            DESTINATION ${CATKIN_PACKAGE_PYTHON_DESTINATION})

endif()
