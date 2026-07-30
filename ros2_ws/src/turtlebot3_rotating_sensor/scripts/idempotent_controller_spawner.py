#!/usr/bin/env python3

"""Run the Humble controller spawner with idempotent load recovery."""

import sys

from controller_manager import spawner
from controller_manager.controller_manager_services import service_caller
from controller_manager_msgs.srv import LoadController


SERVICE_TIMEOUT_SEC = 30.0


def _confirmed_loaded(node, controller_manager, controller_name):
    return spawner.is_controller_loaded(
        node,
        controller_manager,
        controller_name,
        SERVICE_TIMEOUT_SEC,
        SERVICE_TIMEOUT_SEC,
    )


def idempotent_load_controller(
    node,
    controller_manager,
    controller_name,
    *,
    service_call=service_caller,
    loaded_check=_confirmed_loaded,
):
    """Issue one load request and accept a confirmed response-loss success."""
    request = LoadController.Request()
    request.name = controller_name
    response = None
    load_error = None
    try:
        response = service_call(
            node,
            f'{controller_manager}/load_controller',
            LoadController,
            request,
            SERVICE_TIMEOUT_SEC,
            SERVICE_TIMEOUT_SEC,
            max_attempts=1,
        )
    except RuntimeError as exc:
        load_error = exc

    if response is not None and response.ok:
        return response
    if loaded_check(node, controller_manager, controller_name):
        node.get_logger().warning(
            'controller load response was unavailable, but '
            f'{controller_name} is confirmed loaded; continuing '
            'idempotently'
        )
        recovered = LoadController.Response()
        recovered.ok = True
        return recovered
    if load_error is not None:
        raise load_error
    raise RuntimeError(
        f'controller {controller_name} was not confirmed loaded'
    )


def main():
    """Substitute only the load operation in the installed Humble spawner."""
    spawner.load_controller = idempotent_load_controller
    return spawner.main()


if __name__ == '__main__':
    sys.exit(main())
