
import gi

# from loguru import logger
from typing import overload, Literal
from enum import Enum

# from fabric.utils.helpers import Enum
from fabric.core.service import Service, Signal, Property

gi.require_version("UPowerGlib", "1.0")
from gi.repository import UPowerGlib as UPower, GObject


class DeviceType(Enum):
    UNKNOWN = 0
    LINE_POWER = 1
    BATTERY = 2
    UPS = 3
    MONITOR = 4
    MOUSE = 5
    KEYBOARD = 6
    PDA = 7
    PHONE = 8
    MEDIA_PLAYER = 9
    TABLET = 10
    COMPUTER = 11
    GAMING_INPUT = 12
    PEN = 13
    TOUCHPAD = 14
    MODEM = 15
    NETWORK = 16
    HEADSET = 17
    SPEAKERS = 18
    HEADPHONES = 19
    VIDEO = 20
    OTHER_AUDIO = 21
    REMOTE_CONTROL = 22
    PRINTER = 23
    SCANNER = 24
    CAMERA = 25
    WEARABLE = 26
    TOY = 27
    BLUETOOTH_GENERIC = 28


class BatteryLevel(Enum):
    UNKNOWN = 0
    NONE = 1
    DISCHARGING = 2
    LOW = 3
    CRITICAL = 4
    NORMAL = 6
    HIGH = 7
    FULL = 8


class BatteryTechnology(Enum):
    UNKNOWN = 0
    LITHIUM_ION = 1
    LITHIUM_POLYMER = 2
    LITHIUM_IRON_PHOSPHATE = 3
    LEAD_ACID = 4
    NICKEL_CADMIUM = 5
    NICKEL_METAL_HYDRIDE = 6


class BatteryState(Enum):
    UNKNOWN = 0
    CHARGING = 1
    DISCHARGING = 2
    EMPTY = 3
    FULLY_CHARGED = 4
    PENDING_CHARGE = 5
    PENDING_DISCHARGE = 6


class PowerDevice(Service):
    _property_mapping: dict[str, str] | None = None

    @Signal
    def removed(self) -> None:
        """When this signal fires, you must finalize this device by removing all references to it."""
        ...

    # meta
    @Property(DeviceType, "readable")
    def type(self) -> DeviceType:
        return DeviceType(self._device.props.kind)

    @Property(str, "readable")
    def vendor(self) -> str:
        return self._device.props.vendor

    @Property(str, "readable")
    def model(self) -> str:
        return self._device.props.model

    @Property(str, "readable")
    def serial_number(self) -> str:
        return self._device.props.serial

    @Property(str, "readable")
    def icon_name(self) -> str:
        return self._device.props.icon_name

    @Property(bool, "readable", default_value=False)
    def connected(self) -> bool:
        return self._device.props.online

    @Property(bool, "readable", default_value=False)
    def online(self) -> bool:
        return self._device.props.online

    @Property(bool, "readable", default_value=False)
    def present(self) -> bool:
        return self._device.props.is_present

    @Property(str, "readable")
    def dbus_path(self) -> str:
        return self._device.get_object_path()

    @Property(str, "readable")
    def native_path(self) -> str:
        return self._device.props.native_path

    @Property(float, "readable", default_value=0.0)
    def temperature(self) -> float:
        return self._device.props.temperature

    # battery
    @Property(BatteryTechnology, "readable")
    def technology(self) -> BatteryTechnology:
        return BatteryTechnology(self._device.props.technology)

    @Property(float, "readable", default_value=0.0)
    def health(self) -> float:
        return self._device.props.capacity

    @Property(int, "readable", default_value=0)
    def charge_cycles(self) -> int:
        return self._device.props.charge_cycles

    @Property(bool, "readable", default_value=False)
    def rechargeable(self) -> bool:
        return self._device.props.is_rechargeable

    @Property(float, "readable", default_value=0.0)
    def percentage(self) -> float:
        if (bl := BatteryLevel(self._device.props.battery_level)) not in (
            BatteryLevel.UNKNOWN,
            BatteryLevel.NONE,
        ):
            return {
                BatteryLevel.CRITICAL: 8.0,
                BatteryLevel.LOW: 20.0,
                BatteryLevel.NORMAL: 50.0,
                BatteryLevel.HIGH: 70.0,
                BatteryLevel.FULL: 100.0,
            }.get(bl, 0.0)  # what? don't you like it?
        return self._device.props.percentage

    @Property(int, "readable", default_value=0)
    def empty_in(self) -> int:
        return self._device.props.time_to_empty

    @Property(int, "readable", default_value=0)
    def full_in(self) -> int:
        return self._device.props.time_to_full

    @Property(BatteryState, "readable")
    def state(self) -> BatteryState:
        return BatteryState(self._device.props.state)

    @classmethod
    def get_property_mapping(cls):
        # bad design at worst, over-engineering at best. it's 4 AM, fuck off.
        if not cls._property_mapping:
            cls._property_mapping = {
                v: k
                for k, v in (
                    {prop.name: prop.name for prop in GObject.list_properties(cls)}
                    | {
                        "full-in": "time-to-full",
                        "empty-in": "time-to-empty",
                        "serial-number": "serial",
                        "present": "is-present",
                        "rechargeable": "is-rechargeable",
                        "connected": "online",
                        "type": "kind",
                    }
                ).items()
            }
        return cls._property_mapping

    def __init__(self, device: UPower.Device, **kwargs):
        super().__init__(**kwargs)
        self._device = device

        self._device.connect("notify", self.do_map_property_notify)

    def __str__(self) -> str:
        return self._device.to_text()

    def do_map_property_notify(self, _, pspec: GObject.ParamSpec):
        if (brdg_prop := self.get_property_mapping().get(pspec.name, None)) is None:
            return
        print("SOURCE PROP CHANGE:", pspec.name, "MAPPED TO:", brdg_prop)
        return self.notify(brdg_prop)


class PowerManager(Service):
    @staticmethod
    def bake_client() -> UPower.Client:
        # bada boom things (compooters)
        err: Exception | None = None
        try:
            client = UPower.Client.new()
        except Exception as e:
            client = None
            err = e
        if not client:
            raise RuntimeError(
                "couldn't establish a connection to UPower, make sure UPower is installed and setup correctly"
                f"\nexception: {err}"
                if err
                else ""
            )
        return client

    @Signal
    def device_added(self, device: PowerDevice):
        return self.notify("devices")

    @Signal
    def device_removed(self, device: PowerDevice):
        device.removed()
        return self.notify("devices")

    @Property(dict[str, PowerDevice], "readable")
    def devices(self) -> dict[str, PowerDevice]:
        return self._devices

    @Property(bool, "readable", default_value=False)
    def lid_present(self) -> bool:
        return self._client.get_lid_is_present()

    @Property(bool, "readable", default_value=False)
    def lid_closed(self) -> bool:
        return self._client.get_lid_is_closed()

    @Property(bool, "readable", default_value=False)
    def battery_powered(self) -> bool:
        return self._client.get_on_battery()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._devices: dict[str, PowerDevice]
        self._default_device: PowerDevice | None = None

        self._client = PowerManager.bake_client()

        self._client.connect("device-added", self.do_register_raw_device)
        self._client.connect("device-removed", self.do_unregister_raw_device)

    @overload
    def get_default_device(self, force: Literal[True]) -> PowerDevice: ...
    @overload
    def get_default_device(self, force: Literal[False] = ...) -> PowerDevice | None: ...

    def get_default_device(self, force: bool = False) -> PowerDevice | None:
        if (
            not (self._client.get_devices2() or self._client.get_on_battery())
            and not force
        ):
            return None

        self._default_device = self._default_device or PowerDevice(
            self._client.get_display_device()
        )
        return self._default_device

    def do_register_raw_device(self, _, device: UPower.Device):
        wrapped_dev = PowerDevice(device)
        self._devices[wrapped_dev.dbus_path] = wrapped_dev
        return self.device_added(wrapped_dev)

    def do_unregister_raw_device(self, _, dbus_path: str):
        if not (dev := self._devices.pop(dbus_path, None)):
            return
        return self.device_removed(dev)


if __name__ == "__main__":
    from gi.repository import Gtk

    def print_device(_, device: PowerDevice):
        print(
            f"{device.dbus_path}:\n  {'\n  '.join([x.strip() for x in str(pm.get_default_device(True)).splitlines()])}\n----"
        )

    pm = PowerManager()
    pm.device_added.connect(print_device)

    print("BATTERY POWERED:", pm.battery_powered)
    print("LID EXISTS:", pm.lid_present, "CLOSED:", pm.lid_closed)
    print("UNDETECTED DEVICES:", pm._client.get_devices())
    print("ALT UNDETECTED DEVICES:", pm._client.get_devices2())
    print_device(None, pm.get_default_device(True))

    Gtk.main()

