"""Trannegry data collector."""

import binascii
import logging
import socket

from homeassistant.exceptions import HomeAssistantError

logger = logging.getLogger(__name__)


class ReadTrannergyDataError(HomeAssistantError):
    """Error reading trannergy data."""


class TrannergyConnectionError(HomeAssistantError):
    """Error connecting to trannergy."""


class ReadTrannergyData:
    """Trannegry datas collector class."""

    def __init__(
        self,
        inverter_ip: str,
        inverter_port: int,
        inverter_serial: str,
        device_serial_number: str,
        enable_3_phase: bool,
    ) -> None:
        """Init."""
        self.__sock = None

        # IP address of the inverter's Wi-Fi module
        self.inverter_ip = inverter_ip

        # Port number the internal server listens on, defaults to 8899 (See inverter web gui: Advanced -> Port settings)
        self.inverter_port = inverter_port

        # Inverter serial number (See inverter web gui: Status -> Connected inverter)
        self.inverter_serial = inverter_serial

        # Device serial number of the Wi-Fi module (See inverter web gui: Status -> Device information)
        self.device_serial_number = device_serial_number

        # Set to True when you have a 3-phase inverter
        self.enable_3_phase = enable_3_phase

    def __socket_connect(self):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.connect((self.inverter_ip, self.inverter_port))

    @staticmethod
    def __request_string(device_serial: str):
        """Create request string."""

        # Reference https://github.com/jbouwh/omnikdatalogger/blob/dev/apps/omnikdatalogger/omnik/InverterMsg.py
        # The request string is build from several parts. The first part is a
        # fixed 4 char string; the second part is the reversed hex notation of
        # the Wi-Fi logger s/n twice; then again a fixed string of two chars; a checksum of
        # the double s/n with an offset; and finally a fixed ending char.

        request_string = b"\x68\x02\x40\x30"

        doublehex = hex(int(device_serial))[2:] * 2
        hexlist = [
            bytes.fromhex(doublehex[i : i + 2])
            for i in reversed(range(0, len(doublehex), 2))
        ]

        cs_count = 115 + sum([ord(c) for c in hexlist])
        cs = bytes.fromhex(hex(cs_count)[-2:])
        request_string += b"".join(hexlist) + b"".join([b"\x01\x00", cs, b"\x16"])
        return request_string

    def __read_serial(self):
        # Send request to the inverter
        self.__sock.sendall(self.__request_string(self.device_serial_number))

        # Receive data
        rawdata = self.__sock.recv(1024)
        serial = str(rawdata[15:31], encoding="UTF-8")

        if serial != self.inverter_serial:
            raise ReadTrannergyDataError(f"Incorrect inverter serial={serial}")

        # convert to more readable
        telegram_data = binascii.hexlify(rawdata)

        # Often, a zero length message is received
        # A valid payload is 206 bytes
        if len(telegram_data) >= 206:
            return f"{telegram_data}"

        raise ReadTrannergyDataError("Empty telegram data")

    def __decode_telegrams(self, telegram_data: str):
        if telegram_data == "":
            raise ReadTrannergyDataError("Cannot decode empty telegram data")

        offset = 2

        data = {}
        data["msg"] = telegram_data[24 + offset : 28 + offset]
        data["serial"] = binascii.unhexlify(
            telegram_data[30 + offset : 62 + offset]
        ).decode("utf-8")
        data["temperature"] = (
            float(int(telegram_data[62 + offset : 66 + offset], 16)) / 10.0
        )
        data["voltage_pv1"] = (
            float(int(telegram_data[66 + offset : 70 + offset], 16)) / 10.0
        )
        data["voltage_pv2"] = (
            float(int(telegram_data[70 + offset : 74 + offset], 16)) / 10.0
        )
        data["voltage_pv3"] = float(int(telegram_data[74:78], 16)) / 10.0
        data["ampere_pv1"] = (
            float(int(telegram_data[78 + offset : 82 + offset], 16)) / 10.0
        )
        data["ampere_pv2"] = (
            float(int(telegram_data[82 + offset : 86 + offset], 16)) / 10.0
        )
        data["ampere_pv3"] = float(int(telegram_data[86:90], 16)) / 10.0
        data["ampere_ac1"] = int(telegram_data[90 + offset : 94 + offset], 16) / 10.0
        data["ampere_ac2"] = float(int(telegram_data[94:98], 16)) / 10.0
        data["ampere_ac3"] = float(int(telegram_data[98:102], 16)) / 10.0
        data["voltage_ac1"] = (
            float(int(telegram_data[102 + offset : 106 + offset], 16)) / 10.0
        )
        data["voltage_ac2"] = float(int(telegram_data[106:110], 16)) / 10.0
        data["voltage_ac3"] = float(int(telegram_data[110:114], 16)) / 10.0
        data["frequency_ac"] = (
            float(int(telegram_data[114 + offset : 118 + offset], 16)) / 100.0
        )
        data["power_ac1"] = int(telegram_data[118 + offset : 122 + offset], 16)
        data["power_ac2"] = float(int(telegram_data[122:126], 16))
        data["power_ac3"] = float(int(telegram_data[126:130], 16))
        data["yield_today"] = int(telegram_data[138 + offset : 142 + offset], 16) * 10
        data["yield_total"] = int(telegram_data[142 + offset : 150 + offset], 16) * 100
        data["hrs_total"] = int(telegram_data[150 + offset : 158 + offset], 16)
        data["runstate"] = int(telegram_data[158 + offset : 160 + offset], 16)
        data["GVFault_1"] = int(telegram_data[162 + offset : 164 + offset], 16)
        data["GVFault_2"] = int(telegram_data[166 + offset : 168 + offset], 16)
        data["GZFault"] = int(telegram_data[170 + offset : 172 + offset], 16)
        data["TmpFault"] = int(telegram_data[174 + offset : 176 + offset], 16)
        data["PVFault"] = int(telegram_data[178 + offset : 180 + offset], 16)
        data["GFCIFault"] = int(telegram_data[182 + offset : 184 + offset], 16)

        # Reference
        # https://github.com/XtheOne/Inverter-Data-Logger/blob/master/InverterMsg.py
        #
        #    1: 1,  # len(1)
        #    2: 12,  # msg(12)
        #    3: 15,  # id(15)
        #    4: 31,  # temperature(31)
        #    5: 33,  # v_pv(33,35,37)
        #    6: 39,  # i_pv(39,41,43)
        #    7: 45,  # i_ac(45,47,49)
        #    8: 51,  # v_ac(51,53,55)
        #    9: 57,  # f_ac(57,62,65)
        #    10: 59,  # p_ac(59,63,67)
        #    11: 69,  # e_today(69)
        #    12: 71,  # e_total(71)
        #    13: 75,  # h_total(75)
        #    14: 79,  # run_state(79)
        #    15: 81,  # GVFaultValue(81)
        #    16: 83,  # GVFaultValue(83)
        #    17: 85,  # GZFaultValue(85)
        #    18: 87,  # TmpFaultValue(87)
        #    19: 89,  # PVFaultValue(89)
        #    20: 91,  # GFCIFaultValue(91)
        #    21: 93,  # errorMsg(93)
        #    22: 101,  # main_fwver(101)
        #    23: 121, }  # slave_fwver(121)

        return data

    def getdata(self) -> dict:
        """GetData."""
        self.__socket_connect()
        telegram = self.__read_serial()
        return self.__decode_telegrams(telegram)
