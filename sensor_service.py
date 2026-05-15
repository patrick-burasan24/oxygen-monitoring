import asyncio
from queue import Queue
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.framer import FramerType
from config import get_env

class SensorService():

    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue

    async def poll_sensor(self):
        while True:
            sensor_ip = get_env("SENSOR_IP", "192.168.0.7")
            sensor_port = int(get_env("SENSOR_PORT", "502"))
            device_id = int(get_env("DEVICE_ID", "1"))

            if not sensor_ip:
                print("Error: No IP address was provided for the sensor.")
                return
        
            client = AsyncModbusTcpClient(
                host=sensor_ip,
                port=sensor_port,
                framer=FramerType.RTU,
                timeout=2
            )

            register_address = get_env("REGISTER_ADDRESS")
            register_count = get_env("REGISTER_COUNT")

            if not register_address or not register_count:
                print("Error: Unconfigured register data. Reading operation cannot commence.")
                return
            
            register_address = int(register_address)
            register_count = int(register_count)
            
            try:
                if not client.connected:
                    await client.connect()

                if client.connected:
                    result = await client.read_holding_registers(
                        address=register_address,
                        count=register_count,
                        device_id=device_id
                    )
                
                    if result.isError():
                        print("Error: An unknown error occured when reading the " \
                        "holding registers.")
                        client.close()
                    else:
                        o2_value = client.convert_from_registers(
                            result.registers[0:2],
                            client.DATATYPE.FLOAT32,
                            word_order="big"
                        )

                        internal_temperaure_value = client.convert_from_registers(
                            result.registers[2:4],
                            client.DATATYPE.FLOAT32,
                            word_order="big"
                        )

                        internal_pressure_value = client.convert_from_registers(
                            result.registers[4:6],
                            client.DATATYPE.FLOAT32,
                            word_order="big",
                        )

                        self.data_queue.put({
                            "o2_value": o2_value,
                            "internal_temperature_value": internal_temperaure_value,
                            "internal_pressure_value": internal_pressure_value,
                        })
                else:
                    print("Error: Connection failed.")

            except Exception as e:
                print(f"Error: {e}")

            await asyncio.sleep(1)