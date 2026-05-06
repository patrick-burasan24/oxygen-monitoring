import asyncio
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.framer import FramerType
import os
from dotenv import load_dotenv

async def monitor_sensor():
    """Display the live data from the sensor"""
    # Setup the connection
    client = AsyncModbusTcpClient(
        host="192.168.0.7",
        port=502,
        framer=FramerType.RTU,
        timeout=10,
    )

    print("Connecting to SINTESY sensor...")
    await client.connect()

    if not client.connected:
        print("Failed to connect.")
        return
    
    print("----- LIVE MONITOR STARTING -----")
    
    try:
        while True:
            # Read 6 integers starting at 10 (Oxygen, Temp, Pressure)
            result = await client.read_holding_registers(
                address=10,
                count=6,
                device_id=2,
            )

            if not result.isError():
                o2 = client.convert_from_registers(
                    result.registers[0:2],
                    client.DATATYPE.FLOAT32,
                    word_order="big",
                )

                temp = client.convert_from_registers(
                    result.registers[2:4],
                    client.DATATYPE.FLOAT32,
                    word_order="big",
                )

                press = client.convert_from_registers(
                    result.registers[4:6],
                    client.DATATYPE.FLOAT32,
                    word_order="big",
                )

                print(f"O2: {o2:.2f}% | Temp: {temp:.1f}°C | Pressure: {press:.0f} mbar", end="\r")
            else:
                print("\nError reading data.")
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Monitor.")
    finally:
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
        monitor_sensor()
    )