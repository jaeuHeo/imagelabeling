import numpy as np


def solution(s):
    res_list = []
    for x in range(1, int(len(s) / 2) + 1):
        ans_list = []
        c_list = []
        count = 0
        for i in range(0, int(len(s)), x):
            split_s = s[i:i + x]

            if i == 0:
                ans_list.append(split_s)
            else:
                if split_s != ans_list[-1]:
                    ans_list.append(split_s)
                    c_list.append('a')
                else:
                    # ans_list.append(int(1))
                    c_list.append(int(1))
        for idx,c in enumerate(c_list):
            if idx>0:

                if type(c) is str:
                    # print('sttr')
                    del c_list[idx]
                    print(c_list)
                else:
                    if type(c_list[idx-1]) is int:
                        # print('int')
                        del c_list[idx]
                    else:
                        pass
        # print(c_list)
        res_list.append(len(''.join([a for a in ans_list]))+len(c_list))


    max_re = min(res_list)
    # answer = min(len_reslist)
    answer = max_re
    return answer

ans = solution("abcabcabcabcdededededede")
print(ans)