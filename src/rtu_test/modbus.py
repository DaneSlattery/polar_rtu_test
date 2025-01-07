from pymodbus.client import ModbusSerialClient
import serial
import serial.tools
import serial.tools.list_ports
# from pymodbus.client.serial import


def enumerature_tty():
    ports = serial.tools.list_ports.comports()
    return ports


def connect(tty) -> ModbusSerialClient:
    client = ModbusSerialClient(tty, baudrate=9600)
    return client


def set_output_1(client: ModbusSerialClient, value):
    result = client.write_register(1000, value)

    print(result.isError())


def read_input_1(client: ModbusSerialClient) -> int:
    result = client.read_holding_registers(200)

    print(result)

    return result.registers[0]
