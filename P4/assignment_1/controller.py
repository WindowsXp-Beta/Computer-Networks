from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_p4runtime_API import SimpleSwitchP4RuntimeAPI # Not needed anymore
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI

import time

topo = load_topo('topology.json')
controllers = {}

# Note: we now use the SimpleSwitchThriftAPI to communicate with the switches
# and not the P4RuntimeAPI anymore.
for p4switch in topo.get_p4switches():
    thrift_port = topo.get_thrift_port(p4switch)
    controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)

# The following lines enable the forwarding as required for assignment 0.
controllers['s1'].table_add('repeater', 'forward', ['1'], ['2'])
controllers['s1'].table_add('repeater', 'forward', ['3'], ['1'])

controllers['s2'].table_add('repeater', 'forward', ['1'], ['2'])
controllers['s2'].table_add('repeater', 'forward', ['2'], ['1'])

controllers['s4'].table_add('repeater', 'forward', ['1'], ['2'])
controllers['s4'].table_add('repeater', 'forward', ['2'], ['1'])

controllers['s3'].table_add('repeater', 'forward', ['1'], ['2'])
controllers['s3'].table_add('repeater', 'forward', ['2'], ['3'])

active_counter = 1
switches = [f's{idx}' for idx in range(1, 5)]
links = [('s1', 's2'), ('s2', 's3'), ('s4', 's1'), ('s3', 's4')]
drop_stat = {}

def print_link(s1, s2):
    # We recommend to implement a function that prints the value of the
    # counters used for a particular link and direction.
    # It will help you to debug.
    # However, this is not mandatory. If you do not do it,
    # we won't deduct points.
    print(f'active counter is {active_counter}')
    for s in switches:
        ctrl = controllers[s]
        print(f'{s}: ingress regs are [{[ctrl.register_read(f"ingress_regs_0", i) for i in range(3)]}, {[ctrl.register_read("ingress_regs_1", i) for i in range(3)]}];\t'
              f'egress regs are [{[ctrl.register_read(f"egress_regs_0", i) for i in range(3)]}, {[ctrl.register_read("egress_regs_1", i) for i in range(3)]}]')


def check_line_and_reset(s_from: str, s_to: str):
    egress_regs = f'egress_regs_{1 - active_counter}'
    ingress_regs = f'ingress_regs_{1 - active_counter}'
    from_port = topo.node_to_node_port_num(s_from, s_to)
    to_port = topo.node_to_node_port_num(s_to, s_from)
    from_port -= 1
    to_port -= 1

    s_from_pkt_cnt = float(controllers[s_from].register_read(egress_regs, from_port))
    controllers[s_from].register_write(egress_regs, from_port, 0)
    s_to_pkt_cnt = float(controllers[s_to].register_read(ingress_regs, to_port))
    controllers[s_to].register_write(ingress_regs, to_port, 0)
    # print(f'{s_from}: {from_port + 1} {s_from_pkt_cnt} to {s_to}: {to_port + 1} {s_to_pkt_cnt}')
    if s_from_pkt_cnt == 0:
        s_from_pkt_cnt = 1
        assert s_to_pkt_cnt == 0, f'The value is {s_to_pkt_cnt}.\tFrom {s_from} to {s_to}.'
        s_to_pkt_cnt = 1
    return s_from_pkt_cnt == s_to_pkt_cnt, s_to_pkt_cnt, s_from_pkt_cnt

def update_active_counter(s: str):
    controllers[s].register_write('active_counter', 0, active_counter)

def init():
    for s in switches:
        ctrl = controllers[s]
        for i in range(3):
            ctrl.register_write("ingress_regs_0", i, 0)
            ctrl.register_write("ingress_regs_1", i, 0)
            ctrl.register_write("egress_regs_0", i, 0)
            ctrl.register_write("egress_regs_1", i, 0)
        update_active_counter(s)

init()
while True:

    # This is where you need to write most of your code.
    # print_link(1, 2)
    try:
        for s_from, s_to in links:
            correct, s_to_pkt_cnt, s_from_pkt_cnt = check_line_and_reset(s_from, s_to)
            stat = drop_stat.setdefault((s_from, s_to), [0 for i in range(2)])
            stat[0] += s_to_pkt_cnt
            stat[1] += s_from_pkt_cnt
            if not correct:
                print(f'The pkt drop percentage of {s_from} to {s_to} is {(1 - s_to_pkt_cnt / s_from_pkt_cnt) * 100} %')

        active_counter = 1 - active_counter
        for s in switches:
            update_active_counter(s)
        print(f'======{active_counter}=======')
        time.sleep(1)
    except KeyboardInterrupt:
        print('*** Statistical Result ***')
        for (s_from, s_to), v in drop_stat.items():
            if v[0] != v[1]:
                print(f'{s_from} to {s_to} has issues. The packet drop rate is {(1 - v[0] / v[1]) * 100}%')
        exit(0)