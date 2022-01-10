import gdb
func_list = gdb.execute("info functions", True, True)
lines = func_list.split('\n')
result = []
for line in lines:
    func_name = line.split(' ')[-1]
    if "@plt" in func_name:
        result.append(func_name[:-4])

with open("function_list.result", "w") as fd:
    result.sort()
    for func in result:
        fd.write(func + '\n')