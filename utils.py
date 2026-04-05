import logging

# States that trigger a Domoticz widget update
stateSet = {
    "core:ClosureState",
    "core:OpenClosedState",
    "core:LuminanceState",
    "core:DeploymentState"
}

# Supported uiClasses for io:// and rts:// devices
_SUPPORTED_IO_CLASSES = {
    "RollerShutter",
    "LightSensor",
    "ExteriorScreen",
    "Screen",
    "Awning",
    "Pergola",
    "GarageDoor",
    "Gate",
    "Window",
    "VenetianBlind",
    "ExteriorVenetianBlind"
}

def filter_devices(Data):
    logging.debug("start filter devices")

    if not any("uiClass" in str(d.get("definition", {})) for d in Data):
        logging.error("filter_devices: missing uiClass in response")
        logging.debug(str(Data))
        return []

    filtered_devices = []
    for device in Data:
        ui_class  = device["definition"]["uiClass"]
        device_url = device["deviceURL"]
        logging.debug("filter_devices: Device name: " + device["label"] + " Device class: " + ui_class)

        is_io_or_rts = device_url.startswith("io://") or device_url.startswith("rts://")
        is_supported_io = ui_class in _SUPPORTED_IO_CLASSES and is_io_or_rts
        is_pod = ui_class == "Pod" and device_url.startswith("internal://")

        if is_supported_io or is_pod:
            filtered_devices.append(device)
            logging.debug("supported device found: " + str(device))
        else:
            logging.debug("unsupported device found: " + str(device))

    logging.debug("finished filter devices")
    return filtered_devices


def filter_events(Data):
    """Filters relevant (DeviceStateChangedEvent / DeviceState) events out of an events list."""
    logging.debug("start filter events")
    filtered_events = []

    for event in Data:
        if event["name"] in ("DeviceStateChangedEvent", "DeviceState"):
            logging.debug(
                "get_events: add event: URL: '" + event["deviceURL"] +
                "' num states: '" + str(len(event["deviceStates"])) + "'"
            )
            for event_state in event["deviceStates"]:
                logging.debug(
                    "   get_events: eventname: '" + event_state["name"] +
                    "' with value: '" + str(event_state["value"]) + "'"
                )
            filtered_events.append(event)

    logging.debug("finished filter events")
    return filtered_events


def filter_states(Data):
    """Filters relevant state data from a device setup API reply."""
    logging.debug("start filter states")
    filtered_states = []

    for device in Data:
        device_url   = device["deviceURL"]
        device_class = device["definition"]["uiClass"]

        if "states" not in device:
            continue

        state_list = [
            state for state in device["states"]
            if state["name"] in stateSet
        ]

        if state_list:
            filtered_states.append({
                "deviceURL":    device_url,
                "deviceStates": state_list,
                "deviceClass":  device_class,
                "name":         "DeviceState"
            })
            logging.debug("Device state: " + str(filtered_states[-1]))

    return filtered_states

