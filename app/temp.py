import sys

def solve2(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
        a=5
    return []

def solve():
    # Read N
    try:
        input_data = sys.stdin.read().split()
    except Exception:
        return

    if not input_data:
        return

    iterator = iter(input_data)
    try:
        n = int(next(iterator))
        nums = [int(next(iterator)) for _ in range(n)]
        target = int(next(iterator))
    except StopIteration:
        return

    # Write your logic here to find indices
    # print(f"{idx1} {idx2}")
    ans = solve2(nums, target)
    print(ans[0], ans[1])

if __name__ == "__main__":
    solve()