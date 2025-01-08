from pymodbus.client import AsyncModbusSerialClient
from pymodbus import FramerType

from enum import Enum
import serial
import serial.tools
import serial.tools.list_ports
# from pymodbus.client.serial import


PC_REGISTER_OFFSET = 300
ANALOG_REGISTER_OFFSET = 400
IN_REGISTER_OFFSET = 500
OUT_REGISTER_OFFSET = 600
PULSE_OUT_REGISTER_OFFSET = (700 -1) # no all option
OUT_CONFIG_REGISTER_OFFSET = 650 -1 #no all option

def enumerature_tty():
    ports = serial.tools.list_ports.comports()
    return ports


async def connect(tty) -> AsyncModbusSerialClient:

    client = AsyncModbusSerialClient(tty, baudrate=9600,framer=FramerType.RTU)
    connected = await client.connect()
    if not connected:
        raise ConnectionError(f"{tty} failed to connect")
    return client


class GPIO(Enum):
    ALL = 0
    IO1 = 1
    IO2 = 2
    IO3 = 3
    IO4 = 4

class AnalogIn(Enum):
    IO1 = 0
    IO2 = 1
    IO3 = 2
    IO4 = 3

class PulseCounter(Enum):
    IO1 = 0
    IO2 = 1
    
class DigOutDefaultState(Enum):
    OFF=0
    ON = 1
    REMEMBER=2


async def set_digi_output(client:AsyncModbusSerialClient, output_no:GPIO, value=1):
    result = await client.write_register(
        OUT_REGISTER_OFFSET + output_no.value, value)

    return result

async def set_digi_output_config(client: AsyncModbusSerialClient, output_no:GPIO, value: DigOutDefaultState= DigOutDefaultState.REMEMBER):
    if output_no == GPIO.ALL:
        raise Exception("All not a valid option")
    
    result =await client.write_register(
        OUT_CONFIG_REGISTER_OFFSET + output_no.value, value)

    return result.isError()


async def get_digi_output_config(client:AsyncModbusSerialClient, output_no:GPIO):
    if output_no == GPIO.ALL:
        raise Exception("All not a valid option")
    registers= (await client.read_holding_registers(OUT_CONFIG_REGISTER_OFFSET+output_no.value)).registers
    return DigOutDefaultState(registers[0])


async def get_digi_output(client:AsyncModbusSerialClient, output_no:GPIO):
    return  (await client.read_holding_registers(OUT_REGISTER_OFFSET+output_no.value)).registers[0]

async def get_analog_input(client:AsyncModbusSerialClient, input_no:AnalogIn):
    register = (await client.read_holding_registers(ANALOG_REGISTER_OFFSET+input_no.value)).registers[0]
    grad = (20.0/20480.0)
    offset = 4
    return register* grad + offset

async def get_digi_input(client: AsyncModbusSerialClient, input_no: GPIO):
    result =await client.read_holding_registers(IN_REGISTER_OFFSET + input_no.value)
    return result.registers[0]

async def get_pulse_count(client: AsyncModbusSerialClient, input_no: PulseCounter):
    result =await  client.read_holding_registers(IN_REGISTER_OFFSET + input_no.value)
    return result.registers[0]

