// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from ros_esc_interfaces:msg/Timekeeper.idl
// generated code does not contain a copyright notice

#ifndef ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__BUILDER_HPP_
#define ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "ros_esc_interfaces/msg/detail/timekeeper__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace ros_esc_interfaces
{

namespace msg
{

namespace builder
{

class Init_Timekeeper_start_time
{
public:
  explicit Init_Timekeeper_start_time(::ros_esc_interfaces::msg::Timekeeper & msg)
  : msg_(msg)
  {}
  ::ros_esc_interfaces::msg::Timekeeper start_time(::ros_esc_interfaces::msg::Timekeeper::_start_time_type arg)
  {
    msg_.start_time = std::move(arg);
    return std::move(msg_);
  }

private:
  ::ros_esc_interfaces::msg::Timekeeper msg_;
};

class Init_Timekeeper_mode
{
public:
  Init_Timekeeper_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Timekeeper_start_time mode(::ros_esc_interfaces::msg::Timekeeper::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_Timekeeper_start_time(msg_);
  }

private:
  ::ros_esc_interfaces::msg::Timekeeper msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::ros_esc_interfaces::msg::Timekeeper>()
{
  return ros_esc_interfaces::msg::builder::Init_Timekeeper_mode();
}

}  // namespace ros_esc_interfaces

#endif  // ROS_ESC_INTERFACES__MSG__DETAIL__TIMEKEEPER__BUILDER_HPP_
