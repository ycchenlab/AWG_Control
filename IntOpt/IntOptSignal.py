from static_trap import StaticTrap
from complete_control_dev_class import AWG
import json
import numpy as np

# best attempt = 1
attempt = 1
with open(f'./IntOptD/params_{attempt}.json', 'r') as f:
    params = json.load(f)
    ntrap, positions, amplitudes = params['ntrap'], np.array(params['positions']), np.array(params['amplitudes'])
    print(f'Initial ntrap = {ntrap} \n Initial RF amplitudes = {amplitudes}')

test = StaticTrap(ntrap=0, mode='formula')
test.amp = amplitudes
# test.amp[1] = 0
# test.amp[3] = 0
# test.amp[6] = 0
test.get_signal()

with open(test.filename, 'r') as f:
    d = json.load(f)

awg = AWG(time=test.duration)
awg.transfer_data(50, d, 0)
awg.execute()
