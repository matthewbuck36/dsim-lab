// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ros_esc_interfaces:msg/Timekeeper.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__TRAITS_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "ros_esc_interfaces/msg/detail/timekeeper__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace ros_esc_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Timekeeper & msg,
  std::ostream & out)
{
  out << "{";
  // member: mode
  {
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << ", ";
  }

  // member: start_time
  {
    out << "start_time: ";
    rosidl_generator_traits::value_to_yaml(msg.start_time, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Timekeeper & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << "\n";
  }

  // member: start_time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "start_time: ";
    rosidl_generator_traits::value_to_yaml(msg.start_time, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Timekeeper & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace ros_esc_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use ros_esc_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const ros_esc_interfaces::msg::Timekeeper & msg,
  std::ostream & out, size_t indentation = 0)
{
  ros_esc_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use ros_esc_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const ros_esc_interfaces::msg::Timekeeper & msg)
{
  return ros_esc_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<ros_esc_interfaces::msg::Timekeeper>()
{
  return "ros_esc_interfaces::msg::Timekeeper";
}

template<>
inline const char * name<ros_esc_interfaces::msg::Timekeeper>()
{
  return "ros_esc_interfaces/msg/Timekeeper";
}

template<>
struct has_fixed_size<ros_esc_interfaces::msg::Timekeeper>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ros_esc_interfaces::msg::Timekeeper>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ros_esc_interfaces::msg::Timekeeper>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__TRAITS_HPP_
