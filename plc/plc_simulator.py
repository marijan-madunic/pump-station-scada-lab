from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import threading
import time

tank_level = 50
pump_cmd = 0
pump_status = 0
heartbeat = 0
auto_mode = 1
manual_pump_cmd = 0

store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 20)
)

context = ModbusServerContext(slaves=store, single=True)

context[0].setValues(3, 0, [
    tank_level,
    pump_cmd,
    pump_status,
    0,   # alarm_high
    0,   # alarm_low
    heartbeat,
    1,   # auto_mode = AUTO
    0    # manual_pump_cmd = OFF
])

def process_loop():
    global tank_level, pump_cmd, pump_status, heartbeat, auto_mode, manual_pump_cmd

    while True:
        regs = context[0].getValues(3, 6, 2)
        auto_mode = regs[0]
        manual_pump_cmd = regs[1]

        if auto_mode == 1:
            if tank_level < 30:
                pump_cmd = 1
            if tank_level > 95:  #80
                pump_cmd = 0
        else:
            pump_cmd = 1 if manual_pump_cmd == 1 else 0

        pump_status = pump_cmd

        if pump_status == 1:
            tank_level += 2
        else:
            tank_level -= 1

        tank_level = max(0, min(100, tank_level))

        alarm_high = 1 if tank_level > 90 else 0
        alarm_low = 1 if tank_level < 10 else 0

        heartbeat += 1

        context[0].setValues(3, 0, [
            tank_level,
            pump_cmd,
            pump_status,
            alarm_high,
            alarm_low,
            heartbeat,
            auto_mode,
            manual_pump_cmd
        ])

        mode_txt = "AUTO" if auto_mode == 1 else "MANUAL"
        print(
            f"Mode: {mode_txt} | Tank: {tank_level} | Pump: {pump_status} | "
            f"ManualCmd: {manual_pump_cmd} | HB: {heartbeat}"
        )

        time.sleep(2)

threading.Thread(target=process_loop, daemon=True).start()

StartTcpServer(context, address=("0.0.0.0", 5020))
