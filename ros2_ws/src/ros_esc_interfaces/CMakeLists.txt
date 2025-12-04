cmake_minimum_required(VERSION 3.8)
project(ros_esc_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclpy REQUIRED)

# for creating the custom messages in the msg folder
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}

  # add custom messages from msg folder here
  # example: "msg/Example.msg"
  "msg/Timekeeper.msg"
  "msg/StampedFloat64.msg"
  "msg/StampedFloat64MultiArray.msg"
  "msg/StampedString.msg"
  "msg/StampedTransformMultiArray.msg"

  # add custom services from srv folder here
  # example: "srv/Example.srv"


  
  # add any packages that the above messages depend on here
  # for example, in the case that one of the above messages depended
  # on a geometry message, write this below: geometry_msgs
  DEPENDENCIES
  geometry_msgs
 )
ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(
    ament_lint_auto REQUIRED
  )
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
