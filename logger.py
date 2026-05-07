import asyncio
import os
from dotenv import load_dotenv
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.framer import FramerType
import database as db

async def start_logging():
    load_dotenv("./data.env")

    DATABASE_PATH = os.getenv("DATABASE_PATH")
    SENSOR_IP = os.getenv("SENSOR_IP")
    SENSOR_PORT = int(os.getenv("SENSOR_PORT"))
    DEVICE_ID = int(os.getenv("DEVICE_ID"))
    if None in [DATABASE_PATH, SENSOR_IP, SENSOR_PORT, DEVICE_ID]:
        return

    con = db.initialize_db(DATABASE_PATH)
    if con is None:
        print("Couldn't establish a connection to the database.")
        return
    
    client = AsyncModbusTcpClient(host=SENSOR_IP, port=SENSOR_PORT, framer=FramerType.RTU, timeout=10)
    await client.connect()

    if not client.connected:
        return
    
    try:
        while True:
            # Read 6 integers from the sensor registers (3 values divided into 6 FLOATS)
            result = await client.read_holding_registers(address=10, count=6, device_id=DEVICE_ID)
            if not result.isError():
                o2 = client.convert_from_registers(result.registers[0:2], client.DATATYPE.FLOAT32, word_order="big")

                if o2 > 25.0:
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