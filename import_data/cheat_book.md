
# Python DSA Muscle Memory 

**Goal:** Master the syntax and standard library tools required for coding interviews.

**Philosophy:** Python is executable pseudocode. Keep it short.


## 1. Input & Output (Speed)
*Common in OA (Online Assessments) like HackerRank/CodeSignal.*

```python
# 1. Read single integer
n = int(input())

# 2. Read array of integers (Space separated)
# Input: "1 2 3 4"
arr = list(map(int, input().split()))

# 3. Read 2D Array (Matrix)
rows = int(input())
grid = [list(map(int, input().split())) for _ in range(rows)]

# 4. Fast I/O (Rarely needed in interview, good for Competitive Programming)
import sys
input = sys.stdin.readline # Overwrite standard input
s = input().strip() # .strip() removes trailing newline '\n'

```

---

## 2. Core Data Structures & Operations

### A. Lists (Array / Vector / ArrayList)

*Python lists are dynamic arrays.*

```python
nums = [1, 2, 3]

# --- CRUD Operations ---
nums.append(4)          # Add to end: O(1)
nums.insert(1, 99)      # Insert at index: O(n)
val = nums.pop()        # Remove last: O(1)
val = nums.pop(0)       # Remove first: O(n) - AVOID THIS, use deque
nums.remove(99)         # Remove by value: O(n)
del nums[0]             # Remove by index

# --- Slicing (The Superpower) ---
# arr[start : stop : step]
copy_arr = nums[:]      # Shallow Copy
sub = nums[1:4]         # Subarray (indices 1, 2, 3)
rev = nums[::-1]        # Reverse new list

# --- Sorting ---
nums.sort()                 # Sort in-place (Ascending)
nums.sort(reverse=True)     # Sort in-place (Descending)
new_list = sorted(nums)     # Return new sorted list
# Custom Sort (Java Comparator equivalent)
# Sort by length, then by value:
strs = ["apple", "bat", "cat"]
strs.sort(key=lambda x: (len(x), x)) 

# --- 2D Arrays ---
rows, cols = 5, 5
# CORRECT way to init 2D array:
matrix = [[0] * cols for _ in range(rows)] 
# WRONG way (creates references to same row):
# matrix = [[0] * cols] * rows 

```

### B. Strings (Immutable)

*Unlike Java StringBuilder, Python strings are immutable. For heavy modifications, convert to list first.*

```python
s = "racecar"

# --- Basics ---
char = s[0]             # Access
length = len(s)         # Length
sub = s[1:4]            # Substring

# --- Conversions ---
num = 123
s_num = str(num)        # int -> string
i_num = int(s_num)      # string -> int
f_num = float("12.34")  # string -> float

# --- Operations ---
# 'StringBuilder' pattern in Python:
chars = list(s)         # ['r', 'a', 'c'...]
chars[0] = 'f'
res = "".join(chars)    # Join list back to string ("facecar")

# --- Essential Methods ---
s.lower() / s.upper()
s.strip()               # Trim whitespace
s.split(",")            # Split by delimiter
s.replace("old", "new") # Replace (returns new string)
s.find("car")           # Returns index or -1
s.count("r")            # Count occurrences
s.isalpha() / s.isdigit() / s.isalnum()

# --- Formatting ---
name, age = "Alice", 30
msg = f"Name: {name}, Age: {age}" # f-strings (Best practice)

```

### C. Hash Map (Dictionary)

*Key-Value pairs. Keys must be immutable (int, string, tuple).*

```python
d = {} # or dict()

# --- CRUD ---
d["key"] = "value"      # Insert/Update
val = d["key"]          # Access (Throws Error if missing)
val = d.get("key", -1)  # Access (Returns -1 if missing - Safe)
del d["key"]            # Delete
exists = "key" in d     # Check existence (O(1))

# --- Iteration ---
for k in d:             # Keys only
    pass
for v in d.values():    # Values only
    pass
for k, v in d.items():  # Key and Value
    print(k, v)

# --- Dict Comprehension ---
# Create map {1: 1, 2: 4, 3: 9}
squares = {x: x*x for x in range(1, 4)}

```

### D. Hash Set (Set)

*Unique elements only. Unordered.*

```python
s = set()

# --- Operations ---
s.add(1)
s.remove(1)             # Throws error if missing
s.discard(1)            # No error if missing
exists = 1 in s         # O(1) Check

# --- Set Math ---
a = {1, 2, 3}
b = {3, 4, 5}
union = a | b           # {1, 2, 3, 4, 5}
intersect = a & b       # {3}
diff = a - b            # {1, 2} (in a but not b)
sym_diff = a ^ b        # {1, 2, 4, 5} (XOR)

```

### E. Tuples

*Immutable lists. Use as Dictionary Keys or for coordinate pairs.*

```python
point = (10, 20)
x, y = point            # Unpacking
# point[0] = 5          # ERROR: Immutable
mp = { (0,1): "Up" }    # Valid key

```

---

## 3. Specialized Data Structures

### A. Stack (LIFO)

*Just use a List.*

```python
stack = []
stack.append(1)         # Push
top = stack.pop()       # Pop
peek = stack[-1]        # Peek
is_empty = not stack    # Check empty

```

### B. Queue / Deque (FIFO / Double Ended)

*Use `collections.deque`. List is slow for Queues.*

```python
from collections import deque

q = deque([1, 2, 3])
q.append(4)             # Add right
q.appendleft(0)         # Add left
val = q.popleft()       # Pop left (Queue Remove) - O(1)
val = q.pop()           # Pop right

```

### C. Heap (Priority Queue)

*Python has `heapq`. It is a **Min-Heap** by default.*

```python
import heapq

min_h = [3, 1, 4]
heapq.heapify(min_h)          # Convert list to heap in O(n)
heapq.heappush(min_h, 0)      # Push
min_val = heapq.heappop(min_h)# Pop Min

# --- Max Heap Trick ---
# Multiply by -1 to store, multiply by -1 to retrieve
nums = [1, 5, 2]
max_h = []
for n in nums:
    heapq.heappush(max_h, -n)
    
curr_max = -heapq.heappop(max_h)

```

### D. TreeSet / SortedSet Equivalent

*Python has NO native `TreeSet` (Red-Black Tree) in standard lib.
**Interview Strategy:** Maintain a sorted list + Binary Search.*

```python
# Insert into sorted list
import bisect

arr = [1, 3, 5]
# 1. Search (Java: contains)
idx = bisect.bisect_left(arr, 3) 
found = idx < len(arr) and arr[idx] == 3

# 2. Insert (Java: add)
bisect.insort(arr, 4) # Inserts at correct position: O(n)
# arr is now [1, 3, 4, 5]

```

---

## 4. Iteration & Looping

```python
nums = [10, 20, 30]

# 1. Range (Standard)
for i in range(len(nums)):
    print(i, nums[i])

# 2. Enumerate (Index + Value) - VERY COMMON
for i, val in enumerate(nums):
    print(i, val)

# 3. Zip (Iterate two arrays simultaneously)
names = ["A", "B"]
ages = [20, 30]
for name, age in zip(names, ages):
    print(name, age)

# 4. Reverse Loop
for i in range(len(nums) - 1, -1, -1):
    pass
# OR
for val in reversed(nums):
    pass

# 5. While Loop
i = 0
while i < 5:
    if i == 2: continue
    if i == 4: break
    i += 1

```

---

## 5. Math & Bit Manipulation

### Math Operations

```python
import math

val = abs(-5)
mx = max(1, 2, 3)
mn = min(1, 2, 3)
p = pow(2, 3)           # 2^3
p = pow(2, 3, 5)        # (2^3) % 5 (Modular Exponentiation)

root = math.sqrt(25)
c = math.ceil(4.2)      # 5
f = math.floor(4.9)     # 4
g = math.gcd(12, 18)    # 6

# Constants
inf = float('inf')      # Infinity
neg_inf = float('-inf')
pi = math.pi

```

### Bitwise Operations

```python
x = 5  # 0101
y = 3  # 0011

and_val = x & y         # 0001
or_val = x | y          # 0111
xor_val = x ^ y         # 0110
not_val = ~x            # -(x+1)
shift_l = x << 1        # 1010 (Multiply by 2)
shift_r = x >> 1        # 0010 (Divide by 2)

# Checking if kth bit is set
is_set = (x >> k) & 1

# Toggle kth bit
x ^= (1 << k)

# Turn off rightmost set bit (Brian Kernighan's Algorithm)
x = x & (x - 1)

```

---

## 6. Powerful Libraries (`collections`)

*These save massive time in interviews.*

```python
from collections import Counter, defaultdict

# 1. Counter (Frequency Map)
s = "banana"
counts = Counter(s) 
# Result: {'a': 3, 'n': 2, 'b': 1}
print(counts['a'])      # 3
print(counts.most_common(1)) # [('a', 3)]

# 2. DefaultDict (Map with default values)
# Avoids KeyErrors.
adj = defaultdict(list)     # Default value is []
counts = defaultdict(int)   # Default value is 0
adj['A'].append('B')        # No need to check if 'A' exists first!

```

---

## 7. Templates (Memorize These)

### A. Binary Search (`bisect` vs Manual)

```python
# Manual (Standard)
l, r = 0, len(nums) - 1
while l <= r:
    mid = (l + r) // 2
    if nums[mid] == target: return mid
    elif nums[mid] < target: l = mid + 1
    else: r = mid - 1

# Using Bisect (for finding insertion points / boundaries)
import bisect
nums = [1, 2, 2, 2, 3]
# Find first position of 2 (Lower Bound)
idx_l = bisect.bisect_left(nums, 2) # Index 1
# Find position after last 2 (Upper Bound)
idx_r = bisect.bisect_right(nums, 2) # Index 4

```

### B. Tree Traversal (DFS/BFS)

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# DFS (Recursion)
def dfs(node):
    if not node: return
    # Preorder logic
    dfs(node.left)
    # Inorder logic
    dfs(node.right)
    # Postorder logic

# BFS (Level Order)
def bfs(root):
    if not root: return
    q = deque([root])
    while q:
        for _ in range(len(q)): # Process level
            node = q.popleft()
            if node.left: q.append(node.left)
            if node.right: q.append(node.right)

```

### C. Graph (Adjacency List + DFS)

```python
# Build Graph
edges = [[0,1], [1,2], [0,2]]
graph = defaultdict(list)
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u) # Remove if directed

# DFS Iterative
visited = set()
stack = [0]
while stack:
    node = stack.pop()
    if node not in visited:
        visited.add(node)
        for neighbor in graph[node]:
            stack.append(neighbor)

```

### D. Linked List

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# Iterate
curr = head
while curr:
    print(curr.val)
    curr = curr.next

# Dummy Node Technique (Prevents edge cases at head)
dummy = ListNode(0)
dummy.next = head
# Now perform operations, return dummy.next

```

---

## 8. Python Pro Tricks for Interviews

1. **Multiple Assignment (Swapping)**

```python
a, b = 1, 2
a, b = b, a # Swaps in one line! No temp var needed.

```

2. **Unpacking**

```python
arr = [1, 2, 3]
x, y, z = arr # Must match length exactly
x, *mid, z = [1, 2, 3, 4, 5] # x=1, mid=[2,3,4], z=5

```

3. **List Comprehension with IF**

```python
# Get all even numbers squared
evens = [x*x for x in nums if x % 2 == 0]

```

4. **Ternary Operator**

```python
# Java: int x = (cond) ? 10 : 20;
x = 10 if condition else 20

```

5. **Any / All**

```python
# Check if ANY number is positive
if any(n > 0 for n in nums): pass

# Check if ALL numbers are positive
if all(n > 0 for n in nums): pass

```

6. **Comparison Chaining**

```python
if 0 < x < 10: # Instead of: x > 0 and x < 10
    pass

```

```

```