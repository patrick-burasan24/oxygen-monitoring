import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pymodbus.framer import FramerType
from pymodbus.client import AsyncModbusTcpClient

async def monitor_sensor(sensor_ip, sensor_port, device_id):
    """Display the live data from the sensor"""
    # Setup the connection
    client = AsyncModbusTcpClient(
        host=sensor_ip,
        port=sensor_port,
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
                device_id=device_id,
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
        monitor_sensor(sensor_ip, sensor_port, device_id)
    )