// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ros_esc_interfaces:msg/StampedFloat64MultiArray.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64_MULTI_ARRAY__TRAITS_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64_MULTI_ARRAY__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "ros_esc_interfaces/msg/detail/stamped_float64_multi_array__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace ros_esc_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const StampedFloat64MultiArray & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    rosidl_generator_traits::value_to_yaml(msg.header, out);
    out << ", ";
  }

  // member: timestamp
  {
    out << "timestamp: ";
    rosidl_generator_traits::value_to_yaml(msg.timestamp, out);
    out << ", ";
  }

  // member: data
  {
    if (msg.data.size() == 0) {
      out << "data: []";
    } else {
      out << "data: [";
      size_t pending_items = msg.data.size();
      for (auto item : msg.data) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const StampedFloat64MultiArray & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header: ";
    rosidl_generator_traits::value_to_yaml(msg.header, out);
    out << "\n";
  }

  // member: timestamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "timestamp: ";
    rosidl_generator_traits::value_to_yaml(msg.timestamp, out);
    out << "\n";
  }

  // member: data
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.data.size() == 0) {
      out << "data: []\n";
    } else {
      out << "data:\n";
      for (auto item : msg.data) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const StampedFloat64MultiArray & msg, bool use_flow_style = false)
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
  const ros_esc_interfaces::msg::StampedFloat64MultiArray & msg,
  std::ostream & out, size_t indentation = 0)
{
  ros_esc_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use ros_esc_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const ros_esc_interfaces::msg::StampedFloat64MultiArray & msg)
{
  return ros_esc_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<ros_esc_interfaces::msg::StampedFloat64MultiArray>()
{
  return "ros_esc_interfaces::msg::StampedFloat64MultiArray";
}

template<>
inline const char * name<ros_esc_interfaces::msg::StampedFloat64MultiArray>()
{
  return "ros_esc_interfaces/msg/StampedFloat64MultiArray";
}

template<>
struct has_fixed_size<ros_esc_interfaces::msg::StampedFloat64MultiArray>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ros_esc_interfaces::msg::StampedFloat64MultiArray>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ros_esc_interfaces::msg::StampedFloat64MultiArray>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64_MULTI_ARRAY__TRAITS_HPP_
