import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.framer import FramerType
import database as db

async def start_logging():
    env_path = Path(".env")
    load_dotenv(env_path)

    database_path = os.getenv("DATABASE_PATH")
    sensor_ip = os.getenv("SENSOR_IP")
    sensor_port = int(os.getenv("SENSOR_PORT"))
    device_id = int(os.getenv("DEVICE_ID"))
    
    if not database_path:
        print("Couldn't get database path. Aborting here.")
        return
    
    if not sensor_ip:
        print("Couldn't get sensor ip. Aborting here.")
        return
    
    if not sensor_port:
        print("Couldn't get sensor port. Aborting here.")
        return
    
    if not device_id:
        print("Couldn't get device id. Aborting here.")
        return

    con = db.initialize_db(database_path
                           )
    if con is None:
        print("Couldn't establish a connection to the database. Aborting here.")
        return
    
    client = AsyncModbusTcpClient(host=sensor_ip, port=sensor_port, framer=FramerType.RTU, timeout=10)
    await client.connect()

    if not client.connected:
        return
    
    try:
        while True:
            # Read 6 integers from the sensor registers (3 values divided into 6 FLOATS)
            result = await client.read_holding_registers(address=10, count=6, device_id=device_id)
            if not result.isError():
                o2 = client.convert_from_registers(result.registers[0:2], client.DATATYPE.FLOAT32, word_order="big")

                if o2 >= 25.0:
                    print("\007")

                temp = client.convert_from_registers(result.registers[2:4], client.DATATYPE.FLOAT32, word_order="big")
                press = client.convert_from_registers(result.registers[4:6], client.DATATYPE.FLOAT32, word_order="big")

                db.add_reading(con, o2, temp, press)

            else:
                print("\nError reading data.")
            
            await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping logger")
    
    except Exception:
        print("\nAn unknown error has occurred.")

    finally:
        client.close()
        con.close()

if __name__ == "__main__":
    asyncio.run(
        start_logging()
    )