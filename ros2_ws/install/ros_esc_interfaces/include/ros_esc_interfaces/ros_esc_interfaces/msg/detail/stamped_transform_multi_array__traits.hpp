// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from ros_esc_interfaces:msg/StampedTransformMultiArray.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__TRAITS_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "ros_esc_interfaces/msg/detail/stamped_transform_multi_array__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'transform_array'
#include "geometry_msgs/msg/detail/transform__traits.hpp"

namespace ros_esc_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const StampedTransformMultiArray & msg,
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

  // member: transform_array
  {
    if (msg.transform_array.size() == 0) {
      out << "transform_array: []";
    } else {
      out << "transform_array: [";
      size_t pending_items = msg.transform_array.size();
      for (auto item : msg.transform_array) {
        to_flow_style_yaml(item, out);
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
  const StampedTransformMultiArray & msg,
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

  // member: transform_array
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.transform_array.size() == 0) {
      out << "transform_array: []\n";
    } else {
      out << "transform_array:\n";
      for (auto item : msg.transform_array) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const StampedTransformMultiArray & msg, bool use_flow_style = false)
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
  const ros_esc_interfaces::msg::StampedTransformMultiArray & msg,
  std::ostream & out, size_t indentation = 0)
{
  ros_esc_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use ros_esc_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const ros_esc_interfaces::msg::StampedTransformMultiArray & msg)
{
  return ros_esc_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<ros_esc_interfaces::msg::StampedTransformMultiArray>()
{
  return "ros_esc_interfaces::msg::StampedTransformMultiArray";
}

template<>
inline const char * name<ros_esc_interfaces::msg::StampedTransformMultiArray>()
{
  return "ros_esc_interfaces/msg/StampedTransformMultiArray";
}

template<>
struct has_fixed_size<ros_esc_interfaces::msg::StampedTransformMultiArray>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<ros_esc_interfaces::msg::StampedTransformMultiArray>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<ros_esc_interfaces::msg::StampedTransformMultiArray>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_TRANSFORM_MULTI_ARRAY__TRAITS_HPP_
