import asyncio

import pymodbus.client as ModbusClient
from pymodbus import (
    FramerType,
    ModbusException,
    pymodbus_apply_logging_config,
)

import os
from dotenv import load_dotenv

async def run_async_simple_client(comm, host, port, framer=FramerType.RTU):
    """Run async client"""
    # Activate debugging
    pymodbus_apply_logging_config("DEBUG")

    print("Get client")
    client: ModbusClient.ModbusBaseClient
    if comm == "tcp":
        client = ModbusClient.AsyncModbusTcpClient(
            host=host,
            port=port,
            framer=framer,
            timeout=10,
            retries=3,
            source_address=None,
        )
    elif comm == "udp":
        client = ModbusClient.AsyncModbusUdpClient(
            port=port,
            framer=framer,
            timeout=10,
            retries=3,
            source_address=None
        )
    elif comm == "serial":
        client = ModbusClient.AsyncModbusSerialClient(
            port=port,
            framer=framer,
            timeout=10,
            retries=3,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            handle_local_echo=False
        )
    else:
        print(f"Unknown client {comm} selected")
        return
    
    print("Connecting to server...")
    await client.connect()
    # Test client is connected
    assert client.connected

    print("Get and verify data")
    try:
        for i in range(0, 60, 2):
            result = await client.read_holding_registers(address=i, count=2, device_id=2)

            if result.isError():
                print(f"Modbus Device Returned an Error: {result}")
            else:
                sensor_value = client.convert_from_registers(
                    result.registers,
                    data_type=client.DATATYPE.FLOAT32,
                    word_order='big',
                )
                
                if -100 < sensor_value < 10000:
                    print(f"Address {i:02d} -> Raw {result.registers} -> Decoded {sensor_value:.2f}")
                        
    except ModbusException as exc:
        print(f"Network or Modbus crash occurred: {exc}")

    except Exception as exc:
        print(f"An unknown error occurred: {exc}")
        
    finally:
        print("Closing connection...")
        client.close()

if __name__ == "__main__":
    load_dotenv("./data.env")
    
    SENSOR_IP = os.getenv("SENSOR_IP")
    SENSOR_PORT = int(os.getenv("SENSOR_PORT"))
    DEVICE_ID = int(os.getenv("DEVICE_ID"))

    if SENSOR_IP is None or SENSOR_PORT is None or DEVICE_ID is None:
        print("Couldn't get sensor details. Exiting here.")
        exit(1)
    
    assert(SENSOR_IP is not None)
    assert(SENSOR_PORT is not None)
    assert(DEVICE_ID is not None)

    asyncio.run(
        run_async_simple_client("tcp", SENSOR_IP, SENSOR_PORT), debug=True
    )