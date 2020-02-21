"""
simple pytorch example
from https://pytorch.org/tutorials/beginner/Intro_to_TorchScript_tutorial.html
"""
import os
import torch  # This is all you need to use both PyTorch and TorchScript!
print(torch.__version__)

script_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_path, "models")
os.makedirs(model_path, exist_ok=True)

class MyDecisionGate(torch.nn.Module):
    def forward(self, x):
        if x.sum() > 0:
            print(">0")
            return x
        else:
            print("<0")
            return -x

class MyCell(torch.nn.Module):
    def __init__(self, dg):
        super(MyCell, self).__init__()
        self.dg = dg
        self.linear = torch.nn.Linear(4, 4)

    def forward(self, x, h):
        new_h = torch.tanh(self.dg(self.linear(x)) + h)
        return new_h, new_h

def print_net(msg, net, tx, th):
    print(f"========= {msg} =========")
    print(f"tensors:\nx:{tx}\nh:{th}\n")
    print(typeof(net))
    print(f"graph: {net.graph}")
    print(f"code: {net.code}")
    print(f"execute net: {net(tx, th)}")


print("========= Direct call =========")
x = torch.rand(3, 4)
h = torch.rand(3, 4)
my_cell = MyCell(MyDecisionGate())
# print("Direct call", my_cell, x, h)
# print (f"x:{x}\nh:{h}")
# print(my_cell(x, h))
# print_net("Direct call", my_cell, x, h)
print(" ========= jit trace =========")
# Run this multiple times: trace code will change based on condition
# of MyDecisionGate
my_cell = MyCell(MyDecisionGate())
traced_cell = torch.jit.trace(my_cell, (x, h))
#print(traced_cell.graph)
#print(traced_cell)
#print(traced_cell.code)
traced_cell.save(os.path.join(model_path,"model_trace.zip"))
#print(traced_cell(x, h))
print_net("traced", traced_cell, x, h)
print("========= jit script =========")
scripted_gate = torch.jit.script(MyDecisionGate())
print(scripted_gate)
my_cell = MyCell(scripted_gate)
scripted_cell = torch.jit.script(my_cell)
#print(scripted_cell.graph)
print(scripted_cell)
print(scripted_gate.code)
print(scripted_cell.code)
print (f"x:{x}\nh:{h}")
print(scripted_cell(x, h))
scripted_cell.save(os.path.join(model_path, "model_script.zip"))
loaded = torch.jit.load(os.path.join(model_path, "model_script.zip"))
print(loaded)
print(loaded.code)
