n = int(input())
a = [int(input()) for _ in range(n)]
res = 0
for i in range(n):
    for j in range(i +1, n):
        hi, ji = a[i], a[j]
        higherFound = False
        for k in range(i +1, j):
            if a[k] > hi or a[k] > ji:
                higherFound = True
                break
        if not higherFound:
            res += 1
print(res)