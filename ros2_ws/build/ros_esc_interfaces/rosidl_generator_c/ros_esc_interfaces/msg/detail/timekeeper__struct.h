// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from ros_esc_interfaces:msg/Timekeeper.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__STRUCT_H_
#define ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'mode'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/Timekeeper in the package ros_esc_interfaces.
/**
  * This message is used to broadcast timekeeping information 
  * for other ROS nodes to reference. Note that this message
  * communicates the start time of an experiment, and whether
  * timekeeping should be done with Gazebo sim time, or real time.
 */
typedef struct ros_esc_interfaces__msg__Timekeeper
{
  /// The "sim_time" mode tells the ROS nodes to publish their
  /// own timestamps based off Gazebo simulation time, the "real_time"
  /// mode tells the nodes to use real time instead.
  /// Timekeeping mode, either "sim time" or "real time"
  rosidl_runtime_c__String mode;
  /// Start time of the experiment to reference
  double start_time;
} ros_esc_interfaces__msg__Timekeeper;

// Struct for a sequence of ros_esc_interfaces__msg__Timekeeper.
typedef struct ros_esc_interfaces__msg__Timekeeper__Sequence
{
  ros_esc_interfaces__msg__Timekeeper * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} ros_esc_interfaces__msg__Timekeeper__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__STRUCT_H_
