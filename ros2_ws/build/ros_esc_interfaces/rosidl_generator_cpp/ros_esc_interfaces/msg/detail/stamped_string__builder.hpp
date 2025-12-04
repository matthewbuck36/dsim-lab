// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from ros_esc_interfaces:msg/StampedString.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_STRING__BUILDER_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_STRING__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "ros_esc_interfaces/msg/detail/stamped_string__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace ros_esc_interfaces
{

namespace msg
{

namespace builder
{

class Init_StampedString_data
{
public:
  explicit Init_StampedString_data(::ros_esc_interfaces::msg::StampedString & msg)
  : msg_(msg)
  {}
  ::ros_esc_interfaces::msg::StampedString data(::ros_esc_interfaces::msg::StampedString::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedString msg_;
};

class Init_StampedString_timestamp
{
public:
  explicit Init_StampedString_timestamp(::ros_esc_interfaces::msg::StampedString & msg)
  : msg_(msg)
  {}
  Init_StampedString_data timestamp(::ros_esc_interfaces::msg::StampedString::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return Init_StampedString_data(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedString msg_;
};

class Init_StampedString_header
{
public:
  Init_StampedString_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StampedString_timestamp header(::ros_esc_interfaces::msg::StampedString::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_StampedString_timestamp(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedString msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::ros_esc_interfaces::msg::StampedString>()
{
  return ros_esc_interfaces::msg::builder::Init_StampedString_header();
}

}  // namespace ros_esc_interfaces

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_STRING__BUILDER_HPP_
