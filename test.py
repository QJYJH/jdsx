from collections import defaultdict

d = defaultdict(list)
# d['a'].append(1)  # 正常，'a' 不存在，但自动创建了一个空列表
print(d)