// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from ros_esc_interfaces:msg/StampedFloat64.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64__BUILDER_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "ros_esc_interfaces/msg/detail/stamped_float64__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace ros_esc_interfaces
{

namespace msg
{

namespace builder
{

class Init_StampedFloat64_data
{
public:
  explicit Init_StampedFloat64_data(::ros_esc_interfaces::msg::StampedFloat64 & msg)
  : msg_(msg)
  {}
  ::ros_esc_interfaces::msg::StampedFloat64 data(::ros_esc_interfaces::msg::StampedFloat64::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedFloat64 msg_;
};

class Init_StampedFloat64_timestamp
{
public:
  explicit Init_StampedFloat64_timestamp(::ros_esc_interfaces::msg::StampedFloat64 & msg)
  : msg_(msg)
  {}
  Init_StampedFloat64_data timestamp(::ros_esc_interfaces::msg::StampedFloat64::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return Init_StampedFloat64_data(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedFloat64 msg_;
};

class Init_StampedFloat64_header
{
public:
  Init_StampedFloat64_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StampedFloat64_timestamp header(::ros_esc_interfaces::msg::StampedFloat64::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_StampedFloat64_timestamp(msg_);
  }

private:
  ::ros_esc_interfaces::msg::StampedFloat64 msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::ros_esc_interfaces::msg::StampedFloat64>()
{
  return ros_esc_interfaces::msg::builder::Init_StampedFloat64_header();
}

}  // namespace ros_esc_interfaces

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__STAMPED_FLOAT64__BUILDER_HPP_
