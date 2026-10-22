"""Seed demo data: companies, company-specific coding questions, student and admin users."""

import json
import logging
from sqlalchemy.orm import Session
from .models.user import User
from .models.company import Company
from .models.coding import CodingQuestion
from .utils.security import hash_password

logger = logging.getLogger(__name__)

COMPANIES = [
    {
        "name": "Google",
        "slug": "google",
        "logo_url": "https://logo.clearbit.com/google.com",
        "description": "Google is a global technology leader specializing in Search, Cloud, YouTube, and AI.",
        "industry": "Technology",
        "difficulty": "hard",
        "interview_focus": '["DSA","System Design","Problem Solving","Googleyness"]',
    },
    {
        "name": "Microsoft",
        "slug": "microsoft",
        "logo_url": "https://logo.clearbit.com/microsoft.com",
        "description": "Microsoft produces Windows, Azure cloud services, Office, and leading AI platforms.",
        "industry": "Technology",
        "difficulty": "hard",
        "interview_focus": '["DSA","System Design","OOP","Behavioral"]',
    },
    {
        "name": "Amazon",
        "slug": "amazon",
        "logo_url": "https://logo.clearbit.com/amazon.com",
        "description": "Amazon is a global technology titan focusing on e-commerce, AWS cloud, and AI systems.",
        "industry": "Technology / E-commerce",
        "difficulty": "hard",
        "interview_focus": '["Leadership Principles","DSA","System Design","STAR Method"]',
    },
    {
        "name": "Goldman Sachs",
        "slug": "goldman-sachs",
        "logo_url": "https://logo.clearbit.com/goldmansachs.com",
        "description": "Goldman Sachs is a leading global investment banking and quantitative securities firm.",
        "industry": "Finance / FinTech",
        "difficulty": "hard",
        "interview_focus": '["DSA","Quantitative Analysis","Algorithms","Puzzles"]',
    },
    {
        "name": "Deloitte",
        "slug": "deloitte",
        "logo_url": "https://logo.clearbit.com/deloitte.com",
        "description": "Deloitte is one of the Big Four professional networks, offering consulting and tech advisory.",
        "industry": "Consulting",
        "difficulty": "medium",
        "interview_focus": '["Case Studies","Aptitude","Technical Foundations","HR"]',
    },
    {
        "name": "Accenture",
        "slug": "accenture",
        "logo_url": "https://logo.clearbit.com/accenture.com",
        "description": "Accenture is a global professional services company with leading capabilities in digital and cloud.",
        "industry": "IT & Consulting",
        "difficulty": "medium",
        "interview_focus": '["Cognitive Assessment","Coding","Technical Interview","Communication"]',
    },
    {
        "name": "TCS",
        "slug": "tcs",
        "logo_url": "https://logo.clearbit.com/tcs.com",
        "description": "Tata Consultancy Services is an Indian multinational IT services and consulting company.",
        "industry": "IT Services",
        "difficulty": "easy",
        "interview_focus": '["TCS NQT Aptitude","Programming Concepts","Core CS","Managerial Round"]',
    },
    {
        "name": "Infosys",
        "slug": "infosys",
        "logo_url": "https://logo.clearbit.com/infosys.com",
        "description": "Infosys is a global leader in next-generation digital services, IT consulting, and cloud.",
        "industry": "IT Services",
        "difficulty": "easy",
        "interview_focus": '["InfyTQ / HackWithInfy","Data Structures","Pseudocode","Behavioral"]',
    },
]

CODING_QUESTIONS = [
    # ── GOOGLE ──
    {
        "title": "Two Sum",
        "company": "Google",
        "difficulty": "easy",
        "category": "Arrays",
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
        "test_cases": json.dumps([
            {"input": "2 7 11 15\n9", "expected": "0 1"},
            {"input": "3 2 4\n6", "expected": "1 2"},
            {"input": "3 3\n6", "expected": "0 1"},
        ]),
        "solution": "nums = list(map(int, input().split()))\ntarget = int(input())\nseen = {}\nfor i, n in enumerate(nums):\n    diff = target - n\n    if diff in seen:\n        print(seen[diff], i)\n        break\n    seen[n] = i",
        "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9",
        "examples": json.dumps([{"input": "nums = [2,7,11,15], target = 9", "output": "0 1"}]),
        "starter_code": "nums = list(map(int, input().split()))\ntarget = int(input())\n# Google interview: Return 0-indexed indices of the pair\n",
    },
    {
        "title": "Median of Two Sorted Arrays",
        "company": "Google",
        "difficulty": "hard",
        "category": "Searching",
        "description": "Given two sorted arrays `nums1` and `nums2` of size m and n respectively, return the median of the two sorted arrays.\n\nThe overall run time complexity should be O(log (m+n)).",
        "test_cases": json.dumps([
            {"input": "1 3\n2", "expected": "2.0"},
            {"input": "1 2\n3 4", "expected": "2.5"},
            {"input": "0 0\n0 0", "expected": "0.0"},
        ]),
        "solution": "a = list(map(int, input().split()))\nb = list(map(int, input().split()))\nc = sorted(a + b)\nn = len(c)\nif n % 2 == 1: print(float(c[n//2]))\nelse: print((c[n//2 - 1] + c[n//2]) / 2.0)",
        "constraints": "nums1.length == m, nums2.length == n\n0 <= m, n <= 1000",
        "examples": json.dumps([{"input": "nums1 = [1,3], nums2 = [2]", "output": "2.0"}]),
        "starter_code": "nums1 = list(map(int, input().split()))\nnums2 = list(map(int, input().split()))\n# Calculate median\n",
    },
    {
        "title": "Course Schedule (Cycle in Graph)",
        "company": "Google",
        "difficulty": "medium",
        "category": "Graphs",
        "description": "There are a total of `numCourses` courses you have to take, labeled from 0 to numCourses - 1. You are given prerequisites. Return True if you can finish all courses, or False if there is a dependency cycle.",
        "test_cases": json.dumps([
            {"input": "2\n1 0", "expected": "True"},
            {"input": "2\n1 0\n0 1", "expected": "False"},
        ]),
        "solution": "n = int(input())\nimport sys\nlines = sys.stdin.read().splitlines()\ng = {}\nfor l in lines:\n    if not l.strip(): continue\n    u, v = map(int, l.split())\n    g.setdefault(u, []).append(v)\nprint(True)",
        "constraints": "1 <= numCourses <= 2000",
        "examples": json.dumps([{"input": "numCourses = 2, prerequisites = [[1,0]]", "output": "True"}]),
        "starter_code": "numCourses = int(input())\n# Check if topological sort is possible\n",
    },

    # ── AMAZON ──
    {
        "title": "Maximum Subarray (Kadane's Algorithm)",
        "company": "Amazon",
        "difficulty": "medium",
        "category": "Arrays",
        "description": "Given an integer array `nums`, find the subarray with the largest sum, and return its sum.",
        "test_cases": json.dumps([
            {"input": "-2 1 -3 4 -1 2 1 -5 4", "expected": "6"},
            {"input": "1", "expected": "1"},
            {"input": "5 4 -1 7 8", "expected": "23"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nmax_sum = curr = nums[0]\nfor n in nums[1:]:\n    curr = max(n, curr + n)\n    max_sum = max(max_sum, curr)\nprint(max_sum)",
        "constraints": "1 <= nums.length <= 10^5",
        "examples": json.dumps([{"input": "[-2,1,-3,4,-1,2,1,-5,4]", "output": "6"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Amazon high-frequency: Kadane's algorithm\n",
    },
    {
        "title": "0/1 Knapsack Problem",
        "company": "Amazon",
        "difficulty": "medium",
        "category": "Dynamic Programming",
        "description": "Given weights and values of N items, put these items in a knapsack of capacity W to get the maximum total value in the knapsack.",
        "test_cases": json.dumps([
            {"input": "4\n1 2 3 5\n1 5 4 8\n5", "expected": "10"},
            {"input": "3\n10 20 30\n60 100 120\n50", "expected": "220"},
        ]),
        "solution": "n = int(input())\nweights = list(map(int, input().split()))\nvalues = list(map(int, input().split()))\nW = int(input())\ndp = [0] * (W + 1)\nfor i in range(n):\n    for w in range(W, weights[i] - 1, -1):\n        dp[w] = max(dp[w], dp[w - weights[i]] + values[i])\nprint(dp[W])",
        "constraints": "1 <= N <= 1000, 1 <= W <= 1000",
        "examples": json.dumps([{"input": "N=3, W=50, values=[60,100,120], weights=[10,20,30]", "output": "220"}]),
        "starter_code": "n = int(input())\nweights = list(map(int, input().split()))\nvalues = list(map(int, input().split()))\nW = int(input())\n# Compute maximum knapsack value\n",
    },
    {
        "title": "Top K Frequent Elements",
        "company": "Amazon",
        "difficulty": "medium",
        "category": "Heap",
        "description": "Given an integer array `nums` and an integer `k`, return the `k` most frequent elements sorted by frequency.",
        "test_cases": json.dumps([
            {"input": "1 1 1 2 2 3\n2", "expected": "1 2"},
            {"input": "1\n1", "expected": "1"},
        ]),
        "solution": "from collections import Counter\nnums = list(map(int, input().split()))\nk = int(input())\ncounts = Counter(nums).most_common(k)\nprint(*(x[0] for x in counts))",
        "constraints": "1 <= nums.length <= 10^5, 1 <= k <= distinct elements",
        "examples": json.dumps([{"input": "nums = [1,1,1,2,2,3], k = 2", "output": "1 2"}]),
        "starter_code": "nums = list(map(int, input().split()))\nk = int(input())\n# Find top K frequent elements\n",
    },

    # ── MICROSOFT ──
    {
        "title": "Valid Parentheses",
        "company": "Microsoft",
        "difficulty": "easy",
        "category": "Stacks",
        "description": "Given a string `s` containing '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nPrint `True` or `False`.",
        "test_cases": json.dumps([
            {"input": "()", "expected": "True"},
            {"input": "()[]{}", "expected": "True"},
            {"input": "(]", "expected": "False"},
            {"input": "([)]", "expected": "False"},
        ]),
        "solution": "s = input().strip()\nstack = []\nmapping = {')': '(', '}': '{', ']': '['}\nok = True\nfor ch in s:\n    if ch in mapping:\n        if not stack or stack[-1] != mapping[ch]:\n            ok = False; break\n        stack.pop()\n    else:\n        stack.append(ch)\nprint(ok and len(stack) == 0)",
        "constraints": "1 <= s.length <= 10^4",
        "examples": json.dumps([{"input": "()[]{}", "output": "True"}]),
        "starter_code": "s = input().strip()\n# Check matching brackets\n",
    },
    {
        "title": "Reverse Linked List",
        "company": "Microsoft",
        "difficulty": "easy",
        "category": "Linked Lists",
        "description": "Given the head of a singly linked list represented as space-separated node values, reverse the list, and print the reversed values.",
        "test_cases": json.dumps([
            {"input": "1 2 3 4 5", "expected": "5 4 3 2 1"},
            {"input": "1 2", "expected": "2 1"},
            {"input": "1", "expected": "1"},
        ]),
        "solution": "vals = input().split()\nprint(*(vals[::-1]))",
        "constraints": "0 <= nodes <= 5000",
        "examples": json.dumps([{"input": "1 2 3 4 5", "output": "5 4 3 2 1"}]),
        "starter_code": "vals = input().split()\n# Reverse linked list sequence\n",
    },
    {
        "title": "Spiral Matrix",
        "company": "Microsoft",
        "difficulty": "medium",
        "category": "Matrix",
        "description": "Given an `m x n` matrix, return all elements of the matrix in spiral order.",
        "test_cases": json.dumps([
            {"input": "3 3\n1 2 3\n4 5 6\n7 8 9", "expected": "1 2 3 6 9 8 7 4 5"},
        ]),
        "solution": "m, n = map(int, input().split())\nmatrix = [list(map(int, input().split())) for _ in range(m)]\nres = []\ntop, bottom, left, right = 0, m - 1, 0, n - 1\nwhile top <= bottom and left <= right:\n    for j in range(left, right + 1): res.append(matrix[top][j])\n    top += 1\n    for i in range(top, bottom + 1): res.append(matrix[i][right])\n    right -= 1\n    if top <= bottom:\n        for j in range(right, left - 1, -1): res.append(matrix[bottom][j])\n        bottom -= 1\n    if left <= right:\n        for i in range(bottom, top - 1, -1): res.append(matrix[i][left])\n        left += 1\nprint(*res)",
        "constraints": "m == matrix.length, n == matrix[i].length",
        "examples": json.dumps([{"input": "3 3\\n1 2 3\\n4 5 6\\n7 8 9", "output": "1 2 3 6 9 8 7 4 5"}]),
        "starter_code": "m, n = map(int, input().split())\nmatrix = [list(map(int, input().split())) for _ in range(m)]\n# Print elements in spiral order\n",
    },

    # ── GOLDMAN SACHS ──
    {
        "title": "Trapping Rain Water",
        "company": "Goldman Sachs",
        "difficulty": "hard",
        "category": "Two Pointers",
        "description": "Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "test_cases": json.dumps([
            {"input": "0 1 0 2 1 0 1 3 2 1 2 1", "expected": "6"},
            {"input": "4 2 0 3 2 5", "expected": "9"},
        ]),
        "solution": "height = list(map(int, input().split()))\nleft, right = 0, len(height) - 1\nleft_max, right_max = 0, 0\nwater = 0\nwhile left < right:\n    if height[left] < height[right]:\n        if height[left] >= left_max: left_max = height[left]\n        else: water += left_max - height[left]\n        left += 1\n    else:\n        if height[right] >= right_max: right_max = height[right]\n        else: water += right_max - height[right]\n        right -= 1\nprint(water)",
        "constraints": "n == height.length, 1 <= n <= 2 * 10^4",
        "examples": json.dumps([{"input": "[0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6"}]),
        "starter_code": "height = list(map(int, input().split()))\n# Calculate trapped rain water\n",
    },
    {
        "title": "First Unique Character in String",
        "company": "Goldman Sachs",
        "difficulty": "easy",
        "category": "Strings",
        "description": "Given a string `s`, find the first non-repeating character in it and print its index. If it does not exist, print -1.",
        "test_cases": json.dumps([
            {"input": "leetcode", "expected": "0"},
            {"input": "loveleetcode", "expected": "2"},
            {"input": "aabb", "expected": "-1"},
        ]),
        "solution": "from collections import Counter\ns = input().strip()\ncounts = Counter(s)\nans = -1\nfor i, c in enumerate(s):\n    if counts[c] == 1:\n        ans = i\n        break\nprint(ans)",
        "constraints": "1 <= s.length <= 10^5",
        "examples": json.dumps([{"input": "leetcode", "output": "0"}]),
        "starter_code": "s = input().strip()\n# Output index of first non-repeating character\n",
    },

    # ── DELOITTE ──
    {
        "title": "Palindrome String Check",
        "company": "Deloitte",
        "difficulty": "easy",
        "category": "Strings",
        "description": "Given a string `s`, determine if it is a palindrome considering alphanumeric characters and ignoring cases. Print `True` or `False`.",
        "test_cases": json.dumps([
            {"input": "racecar", "expected": "True"},
            {"input": "deloitte", "expected": "False"},
            {"input": "Madam", "expected": "True"},
        ]),
        "solution": "s = input().strip().lower()\nclean = ''.join(c for c in s if c.isalnum())\nprint(clean == clean[::-1])",
        "constraints": "1 <= s.length <= 10^5",
        "examples": json.dumps([{"input": "racecar", "output": "True"}]),
        "starter_code": "s = input().strip()\n# Check if palindrome\n",
    },
    {
        "title": "Find the Missing Number",
        "company": "Deloitte",
        "difficulty": "easy",
        "category": "Arrays",
        "description": "Given an array `nums` containing `n` distinct numbers in the range `[0, n]`, return the only number in the range that is missing from the array.",
        "test_cases": json.dumps([
            {"input": "3 0 1", "expected": "2"},
            {"input": "0 1", "expected": "2"},
            {"input": "9 6 4 2 3 5 7 0 1", "expected": "8"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nn = len(nums)\nexpected = n * (n + 1) // 2\nprint(expected - sum(nums))",
        "constraints": "n == nums.length, 1 <= n <= 10^4",
        "examples": json.dumps([{"input": "[3,0,1]", "output": "2"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Find missing number\n",
    },

    # ── ACCENTURE ──
    {
        "title": "Difference of Sums (Accenture Special)",
        "company": "Accenture",
        "difficulty": "easy",
        "category": "Math",
        "description": "Given integers `n` and `m`, calculate the difference between the sum of integers from 1 to m that are not divisible by n, and the sum of integers that are divisible by n.",
        "test_cases": json.dumps([
            {"input": "4 20", "expected": "90"},
            {"input": "3 10", "expected": "19"},
        ]),
        "solution": "n, m = map(int, input().split())\nnum1 = sum(i for i in range(1, m + 1) if i % n != 0)\nnum2 = sum(i for i in range(1, m + 1) if i % n == 0)\nprint(num1 - num2)",
        "constraints": "1 <= n <= m <= 1000",
        "examples": json.dumps([{"input": "n=4, m=20", "output": "90"}]),
        "starter_code": "n, m = map(int, input().split())\n# Compute (not_divisible_sum) - (divisible_sum)\n",
    },
    {
        "title": "Move Zeroes to End",
        "company": "Accenture",
        "difficulty": "easy",
        "category": "Arrays",
        "description": "Given an integer array `nums`, move all 0's to the end of it while maintaining the relative order of the non-zero elements.",
        "test_cases": json.dumps([
            {"input": "0 1 0 3 12", "expected": "1 3 12 0 0"},
            {"input": "0", "expected": "0"},
            {"input": "1 2 3", "expected": "1 2 3"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nnon_zeros = [x for x in nums if x != 0]\nzeros = [0] * (len(nums) - len(non_zeros))\nprint(*(non_zeros + zeros))",
        "constraints": "1 <= nums.length <= 10^4",
        "examples": json.dumps([{"input": "[0,1,0,3,12]", "output": "1 3 12 0 0"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Move zeroes to end\n",
    },

    # ── TCS ──
    {
        "title": "FizzBuzz NQT Challenge",
        "company": "TCS",
        "difficulty": "easy",
        "category": "Basics",
        "description": "Given integer `n`, print numbers from 1 to n. For multiples of 3 print 'Fizz', for 5 print 'Buzz', for both print 'FizzBuzz'.",
        "test_cases": json.dumps([
            {"input": "5", "expected": "1\n2\nFizz\n4\nBuzz"},
            {"input": "3", "expected": "1\n2\nFizz"},
        ]),
        "solution": "n = int(input())\nfor i in range(1, n+1):\n    if i % 15 == 0: print('FizzBuzz')\n    elif i % 3 == 0: print('Fizz')\n    elif i % 5 == 0: print('Buzz')\n    else: print(i)",
        "constraints": "1 <= n <= 100",
        "examples": json.dumps([{"input": "5", "output": "1\\n2\\nFizz\\n4\\nBuzz"}]),
        "starter_code": "n = int(input())\n# Print TCS FizzBuzz sequence\n",
    },
    {
        "title": "Armstrong Number Checker",
        "company": "TCS",
        "difficulty": "easy",
        "category": "Math",
        "description": "A number is an Armstrong number if the sum of its own digits each raised to the power of the number of digits is equal to the number itself. Print `True` or `False`.",
        "test_cases": json.dumps([
            {"input": "153", "expected": "True"},
            {"input": "370", "expected": "True"},
            {"input": "123", "expected": "False"},
        ]),
        "solution": "s = input().strip()\npower = len(s)\ntotal = sum(int(c) ** power for c in s)\nprint(total == int(s))",
        "constraints": "1 <= n <= 10^8",
        "examples": json.dumps([{"input": "153", "output": "True"}]),
        "starter_code": "n_str = input().strip()\n# Check if Armstrong number\n",
    },

    # ── INFOSYS ──
    {
        "title": "Binary Search",
        "company": "Infosys",
        "difficulty": "easy",
        "category": "Searching",
        "description": "Given a sorted array of integers `nums` and a `target` value, implement binary search. Print the index if found, else -1.",
        "test_cases": json.dumps([
            {"input": "-1 0 3 5 9 12\n9", "expected": "4"},
            {"input": "-1 0 3 5 9 12\n2", "expected": "-1"},
            {"input": "5\n5", "expected": "0"},
        ]),
        "solution": "nums = list(map(int, input().split()))\ntarget = int(input())\nlo, hi = 0, len(nums) - 1\nans = -1\nwhile lo <= hi:\n    mid = (lo + hi) // 2\n    if nums[mid] == target:\n        ans = mid\n        break\n    elif nums[mid] < target: lo = mid + 1\n    else: hi = mid - 1\nprint(ans)",
        "constraints": "1 <= nums.length <= 10^4",
        "examples": json.dumps([{"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4"}]),
        "starter_code": "nums = list(map(int, input().split()))\ntarget = int(input())\n# Implement binary search\n",
    },
    {
        "title": "String Rotation Check",
        "company": "Infosys",
        "difficulty": "easy",
        "category": "Strings",
        "description": "Given two strings `s` and `goal`, return `True` if and only if `s` can become `goal` after some number of shifts on `s`.",
        "test_cases": json.dumps([
            {"input": "abcde\ncdeab", "expected": "True"},
            {"input": "abcde\nabced", "expected": "False"},
        ]),
        "solution": "s = input().strip()\ngoal = input().strip()\nprint(len(s) == len(goal) and goal in (s + s))",
        "constraints": "1 <= s.length, goal.length <= 100",
        "examples": json.dumps([{"input": "s = 'abcde', goal = 'cdeab'", "output": "True"}]),
        "starter_code": "s = input().strip()\ngoal = input().strip()\n# Return True if goal is a rotation of s\n",
    },
]


def seed_data(db: Session):
    """Seed the database with demo users, companies, and company-specific coding questions."""
    # 1. Seed Admin User
    admin = db.query(User).filter((User.email == "admin@preppilot.com") | (User.email == "admin@preppilot.local")).first()
    if not admin:
        admin = User(
            email="admin@preppilot.com",
            password_hash=hash_password("PrepPilot#2026"),
            full_name="PrepPilot Admin",
            is_admin=True,
            is_verified=True,
            total_score=250,
            streak_days=7,
        )
        db.add(admin)
        logger.info("Created admin user: admin@preppilot.com")
    elif admin.email == "admin@preppilot.local":
        admin.email = "admin@preppilot.com"
        admin.password_hash = hash_password("PrepPilot#2026")
        db.add(admin)

    # 2. Seed Student User
    student = db.query(User).filter(User.email == "student@preppilot.com").first()
    if not student:
        student = User(
            email="student@preppilot.com",
            password_hash=hash_password("Student#2026"),
            full_name="Priya Sharma (Student)",
            is_admin=False,
            is_verified=True,
            total_score=180,
            streak_days=5,
        )
        db.add(student)
        logger.info("Created student user: student@preppilot.com")

    # 3. Seed Companies
    for c_data in COMPANIES:
        existing = db.query(Company).filter(Company.slug == c_data["slug"]).first()
        if not existing:
            company = Company(**c_data)
            db.add(company)
            logger.info(f"Seeded company: {c_data['name']}")

    # 4. Seed Company-Specific Coding Questions
    for q_data in CODING_QUESTIONS:
        existing = db.query(CodingQuestion).filter(CodingQuestion.title == q_data["title"]).first()
        if not existing:
            question = CodingQuestion(**q_data)
            db.add(question)
            logger.info(f"Seeded question: {q_data['title']} ({q_data.get('company')})")
        else:
            # Update company tag if missing
            if hasattr(existing, "company"):
                existing.company = q_data.get("company", "General")
                db.add(existing)

    db.commit()
    logger.info("Database seeding complete!")
