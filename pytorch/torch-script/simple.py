"""
simple pytorch example
"""
import torch  # This is all you need to use both PyTorch and TorchScript!
import os
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

print("========= Direct call =========")
x = torch.rand(3, 4)
h = torch.rand(3, 4)
my_cell = MyCell(MyDecisionGate())
print(my_cell)
print(my_cell(x, h))
print(" ========= jit trace =========")
# Run this multiple times: trace code will change based on condition 
# of MyDecisionGate
my_cell = MyCell(MyDecisionGate())
traced_cell = torch.jit.trace(my_cell, (x, h))
# print(traced_cell.graph)
print(traced_cell.code)
traced_cell.save(os.path.join(model_path,"model_trace.zip"))
print("========= jit script =========")
scripted_gate = torch.jit.script(MyDecisionGate())
my_cell = MyCell(scripted_gate)
traced_cell = torch.jit.script(my_cell)
# print(traced_cell.graph)
print(traced_cell.code)
traced_cell(x, h)
traced_cell.save(os.path.join(model_path,"model_script.zip"))