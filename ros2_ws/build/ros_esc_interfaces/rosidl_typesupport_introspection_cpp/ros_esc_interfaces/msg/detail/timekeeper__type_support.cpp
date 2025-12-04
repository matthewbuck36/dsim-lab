// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from ros_esc_interfaces:msg/Timekeeper.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "ros_esc_interfaces/msg/detail/timekeeper__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace ros_esc_interfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void Timekeeper_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) ros_esc_interfaces::msg::Timekeeper(_init);
}

void Timekeeper_fini_function(void * message_memory)
{
  auto typed_message = static_cast<ros_esc_interfaces::msg::Timekeeper *>(message_memory);
  typed_message->~Timekeeper();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember Timekeeper_message_member_array[2] = {
  {
    "mode",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_esc_interfaces::msg::Timekeeper, mode),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "start_time",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(ros_esc_interfaces::msg::Timekeeper, start_time),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers Timekeeper_message_members = {
  "ros_esc_interfaces::msg",  // message namespace
  "Timekeeper",  // message name
  2,  // number of fields
  sizeof(ros_esc_interfaces::msg::Timekeeper),
  Timekeeper_message_member_array,  // message members
  Timekeeper_init_function,  // function to initialize message memory (memory has to be allocated)
  Timekeeper_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t Timekeeper_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Timekeeper_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace ros_esc_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<ros_esc_interfaces::msg::Timekeeper>()
{
  return &::ros_esc_interfaces::msg::rosidl_typesupport_introspection_cpp::Timekeeper_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, ros_esc_interfaces, msg, Timekeeper)() {
  return &::ros_esc_interfaces::msg::rosidl_typesupport_introspection_cpp::Timekeeper_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
