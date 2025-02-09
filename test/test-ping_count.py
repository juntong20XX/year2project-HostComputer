"""
就是测试下下面这段代码
```cpp
int passed = ping_res_chk(Message);

if (passed != 0) {
    return passed;
}

// check times
passed_times = (passed_times << 1) + 1;
uint8_t counting = 0;
for (; passed < 8; passed++) {
    counting += passed_times & ++passed;
    if (counting > 4) {
        return -3;
    }
}
```
"""

passed_times = 0b00000111  # 0 表示 ping 未通过, 1 表示通过

while 1:
    inp = input("(y|n|q)>>>")
    if inp == "q":
        break
    passed_times = passed_times << 1  # 默认未通过
    if inp == "y":
        passed_times += 1  # 本次 ping 通过则 + 1
        print("此回合 ping 通了", bin(passed_times)[2:].rjust(8, "0"))
    else:
        print("此回合没 ping 通", bin(passed_times)[2:].rjust(8, "0"))

    counting = 0
    for passed in range(8):
        counting += (passed_times & (1 << passed)) == 0
        # 规则是超过一半的次数 ping 通, 才 pass
        if counting >= 4:
            print("not passed")
            break
    else:
        print("passed")

    passed_times %= 2**8
