import os
import asyncio
import pymodbus.client as ModbusClient
from dotenv import load_dotenv
from pathlib import Path
from pymodbus import (
    FramerType,
    ModbusException,
    pymodbus_apply_logging_config,
)

async def run_async_simple_client(comm, sensor_ip, sensor_port, device_id, framer=FramerType.RTU):
    """Run async client"""
    # Activate debugging
    pymodbus_apply_logging_config("DEBUG")

    print("Get client")
    client: ModbusClient.ModbusBaseClient
    if comm == "tcp":
        client = ModbusClient.AsyncModbusTcpClient(
            host=sensor_ip,
            port=sensor_port,
            framer=framer,
            timeout=10,
            retries=3,
            source_address=None,
        )
    elif comm == "udp":
        client = ModbusClient.AsyncModbusUdpClient(
            port=sensor_port,
            framer=framer,
            timeout=10,
            retries=3,
            source_address=None
        )
    elif comm == "serial":
        client = ModbusClient.AsyncModbusSerialClient(
            port=sensor_port,
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
    if not client.connected:
        print("Failed to connect.")
        return

    print("----- GET AND VERIFY DATA -----")

    sensor_parameters = {}

    try:
        for i in range(0, 60, 2):
            result = await client.read_holding_registers(address=i, count=2, device_id=device_id)

            if result.isError():
                print(f"Modbus Device Returned an Error: {result}")
            else:
                sensor_value = client.convert_from_registers(
                    result.registers,
                    data_type=client.DATATYPE.FLOAT32,
                    word_order="big",
                )
                
                # The technical documentation stipulated that data from the sensor will always
                # reside in this interval.
                if -100 < sensor_value < 10000:
                    print(f"Address {i:02d} -> Raw {result.registers} -> Decoded {sensor_value:.2f}")
                    # We may assume that no real, useful value is zero
                    if sensor_value != 0.0:
                        sensor_parameters[i] = sensor_value
                        
    except ModbusException as exc:
        print(f"Network or Modbus crash occurred: {exc}")

    except Exception as exc:
        print(f"An unknown error occurred: {exc}")
        
    finally:
        print("\nThe decoded sensor values are (Address:Value)")

        # In order to assess which values are indeed the corresponding sensor
        # parameters that we need, one must check with the physical sensor
        # and link the data shown with the data found using this tool.
        # For the SINTESY S210.smartSensor the data comes int 6
        # FLOAT32 which, if put back together, generate three floating
        # point numbers, namely the recorded oxygen concentration,
        # the internal sensor temperature, and, lastly, the internal
        # sensor pressure. But other junk data may reside in what the
        # diagnostics tool finds and we may not guarantee that there
        # will be exactly three numbers at consecutive addresses, therefore
        # it's recommended to double check with the physical item to
        # assert the discovered addresses.
        
        for address, sensor_value in sensor_parameters.items():
            print(f"{address} : {sensor_value}")
            
        print("\nClosing connection...")
        client.close()

if __name__ == "__main__":
    env_path = Path(".env")
    load_dotenv(env_path)
        
    sensor_ip = os.getenv("SENSOR_IP")
    sensor_port = int(os.getenv("SENSOR_PORT"))
    device_id = int(os.getenv("DEVICE_ID"))

    if not sensor_ip:
        print("Couldn't get sensor ip. Exiting here.")
        exit(1)
    
    if not sensor_port:
        print("Couldn't get sensor port. Exiting here.")
        exit(1)

    if not device_id:
        print("Couldn't get device id. Exiting here.")
        exit(1)
    
    asyncio.run(
        run_async_simple_client("tcp", sensor_ip, sensor_port, device_id), debug=True
    )