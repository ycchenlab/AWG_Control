from static_trap import StaticTrap
from complete_control_dev_class import AWG
import json

test = StaticTrap(ntrap=10, mode='formula')
test.get_signal()

with open(test.filename, 'r') as f:
    d = json.load(f)

awg = AWG(time=test.duration)
awg.transfer_data(50, d, 0)
awg.execute()
