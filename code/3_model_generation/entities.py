from transitions import *
from transitions.extensions import GraphMachine

class IR_Model(object):
    states = ['start', 'end']
    def __init__(self, name):
        self.name = name
        self.machine = GraphMachine(model=self, states=IR_Model.states, initial='start', title=name, show_conditions=True, show_state_attributes=True)

if __name__ == '__main__':
#     transitions = [
#         {'trigger': 'widget1', 'source': 'start', 'dest': 'state1', 'unless': 'aaa'},
#         {'trigger': 'widget2', 'source': 'start', 'dest': 'ICSE',
#          'conditions': ['is_valid', 'is_also_valid']}
#     ]
#     states = [{'name': 'ICSE', 'on_exit': ['resume', 'notify']},
#               {'name': 'final', 'on_enter': 'alert', 'on_exit': 'resume'}]
    model1 = IR_Model('HELLO')
    transition = {'trigger': 'self', 'source': 'start', 'dest': 'start', 'conditions': ['con1', 'con2'], 'label': ['label1']}
    model1.machine.add_transitions(transition)
    conditions = []
    for cond in model1.machine.get_transitions('self', 'start', 'start')[0].conditions:
        conditions.append(cond.func)
    model1.machine.remove_transition('self', 'start', 'start')
    conditions.append('333333')
    model1.machine.add_transition(trigger='self', source='start', dest='start', conditions=conditions)
#     model1.machine.add_state(states)
#     print(model1.machine.get_state('final').name)
    model1.get_graph().draw('my_state_diagram.png', prog='dot')