from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
import time

topo = load_topo('topology.json')
controllers = {}

for p4switch in topo.get_p4switches():
    thrift_port = topo.get_thrift_port(p4switch)
    controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)

controller = controllers['s1']
controller.table_clear('repeater')
controller.table_add('repeater', 'random_forward', ['1'], ['2', '3'])
controller.table_add('repeater', 'forward', ['2'], ['1'])
controller.table_add('repeater', 'forward', ['3'], ['1'])

controller = controllers['s2']
controller.table_clear('repeater')
controller.table_add('repeater', 'forward', ['1'], ['2'])
controller.table_add('repeater', 'forward', ['2'], ['1'])

controller = controllers['s3']
controller.table_clear('repeater')
controller.table_add('repeater', 'random_forward', ['2'], ['1', '3'])
controller.table_add('repeater', 'forward', ['1'], ['2'])
controller.table_add('repeater', 'forward', ['3'], ['2'])

controller = controllers['s4']
controller.table_clear('repeater')
controller.table_add('repeater', 'forward', ['1'], ['2'])
controller.table_add('repeater', 'forward', ['2'], ['1'])


while True:
    # wait for 1 minute
    time.sleep(60)

    # read values of counters in the h1 -> h2 direction
    h1_h2_top_path = controllers['s2'].counter_read('packet_ctr', 0)[1]
    h1_h2_bottom_path = controllers['s4'].counter_read('packet_ctr', 0)[1]
    h1_h2_total = h1_h2_top_path + h1_h2_bottom_path

    # avoid ZeroDivisionError
    if h1_h2_total == 0:
        h1_h2_total = 1

    # compute percentages
    h1_h2_percentage_top = round(h1_h2_top_path / h1_h2_total * 100, 2)
    h1_h2_percentage_bottom = round(h1_h2_bottom_path / h1_h2_total * 100, 2)

    # print the results
    print('Packets from h1 to h2 in the top path:', h1_h2_percentage_top, '%')
    print('Packets from h1 to h2 in the bottom path:', h1_h2_percentage_bottom, '%')

    # TODO 4: calculate and print percentages for h2 -> h1 direction
    h2_h1_top_path = controllers['s2'].counter_read('packet_ctr', 1)[1]
    h2_h1_bottom_path = controllers['s4'].counter_read('packet_ctr', 1)[1]
    h2_h1_total = h2_h1_top_path + h2_h1_bottom_path

    # avoid ZeroDivisionError
    if h2_h1_total == 0:
        h2_h1_total = 1

    # compute percentages
    h2_h1_percentage_top = round(h2_h1_top_path / h2_h1_total * 100, 2)
    h2_h1_percentage_bottom = round(h2_h1_bottom_path / h2_h1_total * 100, 2)

    # print the results
    print('Packets from h2 to h1 in the top path:', h2_h1_percentage_top, '%')
    print('Packets from h2 to h1 in the bottom path:', h2_h1_percentage_bottom, '%')

    # TODO 5: clear the values of the counter arrays
    for s in ['s2', 's4']:
        controllers[s].counter_reset('packet_ctr')