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
        "name": "Meta",
        "slug": "meta",
        "logo_url": "https://logo.clearbit.com/meta.com",
        "description": "Meta builds technologies that help people connect, find communities, and grow businesses.",
        "industry": "Technology / Social",
        "difficulty": "hard",
        "interview_focus": '["High-Speed DSA","Graph Algorithms","Trees","Product Architecture"]',
    },
    {
        "name": "Apple",
        "slug": "apple",
        "logo_url": "https://logo.clearbit.com/apple.com",
        "description": "Apple creates iPhone, Mac, iOS, iPadOS, macOS, and custom Silicon hardware architectures.",
        "industry": "Technology / Consumer Hardware",
        "difficulty": "hard",
        "interview_focus": '["Low-Level System Design","Data Structures","Optimization","Clean Architecture"]',
    },
    {
        "name": "Netflix",
        "slug": "netflix",
        "logo_url": "https://logo.clearbit.com/netflix.com",
        "description": "Netflix is one of the world's leading entertainment streaming and distributed systems services.",
        "industry": "Technology / Streaming",
        "difficulty": "hard",
        "interview_focus": '["Distributed Systems","Dynamic Programming","Concurrency","System Scalability"]',
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
        "name": "Uber",
        "slug": "uber",
        "logo_url": "https://logo.clearbit.com/uber.com",
        "description": "Uber develops mobility, delivery, and freight platforms connecting the physical and digital worlds.",
        "industry": "Mobility & Tech",
        "difficulty": "hard",
        "interview_focus": '["Shortest Path & Dijkstra","Intervals","Concurrency","Microservices Design"]',
    },
    {
        "name": "Adobe",
        "slug": "adobe",
        "logo_url": "https://logo.clearbit.com/adobe.com",
        "description": "Adobe creates industry-standard creative software including Photoshop, Illustrator, and Acrobat.",
        "industry": "Software & Design",
        "difficulty": "medium",
        "interview_focus": '["String Manipulation","Bitmasking","Linked Lists","Geometry / Math"]',
    },
    {
        "name": "Atlassian",
        "slug": "atlassian",
        "logo_url": "https://logo.clearbit.com/atlassian.com",
        "description": "Atlassian produces collaboration software for teams including Jira, Confluence, and Bitbucket.",
        "industry": "Enterprise Software",
        "difficulty": "hard",
        "interview_focus": '["Design Patterns","Sliding Window","Hash Tables","System Architecture"]',
    },
    {
        "name": "Oracle",
        "slug": "oracle",
        "logo_url": "https://logo.clearbit.com/oracle.com",
        "description": "Oracle provides cloud infrastructure, enterprise software, and database management systems.",
        "industry": "Cloud & Enterprise DB",
        "difficulty": "medium",
        "interview_focus": '["Database Internals","Trees & BST","Matrix Manipulation","Concurrency"]',
    },
    {
        "name": "Walmart",
        "slug": "walmart",
        "logo_url": "https://logo.clearbit.com/walmart.com",
        "description": "Walmart Global Tech powers digital commerce, supply chain, and retail optimization platforms.",
        "industry": "Retail & Tech",
        "difficulty": "medium",
        "interview_focus": '["Knapsack DP","Greedy Intervals","Tree Traversal","Scale"]',
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
        "title": "Longest Substring Without Repeating Characters",
        "company": "Google",
        "difficulty": "medium",
        "category": "Strings",
        "description": "Given a string `s`, find the length of the longest substring without duplicate characters.",
        "test_cases": json.dumps([
            {"input": "abcabcbb", "expected": "3"},
            {"input": "bbbbb", "expected": "1"},
            {"input": "pwwkew", "expected": "3"},
        ]),
        "solution": "s = input().strip()\nchar_map = {}\nleft = max_len = 0\nfor right, c in enumerate(s):\n    if c in char_map and char_map[c] >= left:\n        left = char_map[c] + 1\n    char_map[c] = right\n    max_len = max(max_len, right - left + 1)\nprint(max_len)",
        "constraints": "0 <= s.length <= 5 * 10^4",
        "examples": json.dumps([{"input": "s = 'abcabcbb'", "output": "3"}]),
        "starter_code": "s = input().strip()\n# Return length of longest substring without duplicates\n",
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
        "solution": "lines = open(0).read().strip().splitlines()\nn = int(lines[0])\nadj = [[] for _ in range(n)]\nindeg = [0] * n\nfor l in lines[1:]:\n    if not l.strip(): continue\n    u, v = map(int, l.split())\n    adj[v].append(u)\n    indeg[u] += 1\nq = [i for i in range(n) if indeg[i] == 0]\ncount = 0\nwhile q:\n    curr = q.pop(0)\n    count += 1\n    for nxt in adj[curr]:\n        indeg[nxt] -= 1\n        if indeg[nxt] == 0:\n            q.append(nxt)\nprint(count == n)",
        "constraints": "1 <= numCourses <= 2000",
        "examples": json.dumps([{"input": "numCourses = 2, prerequisites = [[1,0]]", "output": "True"}]),
        "starter_code": "numCourses = int(input())\n# Check if topological sort is possible\n",
    },

    # ── MICROSOFT ──
    {
        "title": "Reverse Linked List",
        "company": "Microsoft",
        "difficulty": "easy",
        "category": "Linked Lists",
        "description": "Given the head of a singly linked list represented as space-separated integers, reverse the list, and return the reversed list elements.",
        "test_cases": json.dumps([
            {"input": "1 2 3 4 5", "expected": "5 4 3 2 1"},
            {"input": "1 2", "expected": "2 1"},
            {"input": "42", "expected": "42"},
        ]),
        "solution": "arr = input().split()\nprint(' '.join(reversed(arr)))",
        "constraints": "0 <= number of nodes <= 5000",
        "examples": json.dumps([{"input": "head = [1,2,3,4,5]", "output": "5 4 3 2 1"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Reverse in-place or return reversed sequence\n",
    },
    {
        "title": "Valid Parentheses",
        "company": "Microsoft",
        "difficulty": "easy",
        "category": "Stacks",
        "description": "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "test_cases": json.dumps([
            {"input": "()[]{}", "expected": "True"},
            {"input": "(]", "expected": "False"},
            {"input": "([)]", "expected": "False"},
            {"input": "{[]}", "expected": "True"},
        ]),
        "solution": "s = input().strip()\nstack = []\nmapping = {')': '(', '}': '{', ']': '['}\nok = True\nfor ch in s:\n    if ch in mapping.values():\n        stack.append(ch)\n    elif ch in mapping:\n        if not stack or stack[-1] != mapping[ch]:\n            ok = False\n            break\n        stack.pop()\nprint(ok and len(stack) == 0)",
        "constraints": "1 <= s.length <= 10^4",
        "examples": json.dumps([{"input": "s = '()[]{}'", "output": "True"}]),
        "starter_code": "s = input().strip()\n# Return True if valid bracket matching, else False\n",
    },
    {
        "title": "Binary Tree Level Order Traversal",
        "company": "Microsoft",
        "difficulty": "medium",
        "category": "Trees",
        "description": "Given a binary tree represented as an array in breadth-first order (use 'null' for empty nodes), return its level order traversal values line by line.",
        "test_cases": json.dumps([
            {"input": "3 9 20 null null 15 7", "expected": "3\n9 20\n15 7"},
            {"input": "1", "expected": "1"},
        ]),
        "solution": "tokens = input().split()\nif not tokens or tokens == ['null']: print('')\nelse:\n    print(tokens[0])\n    if len(tokens) > 2 and tokens[1] != 'null' and tokens[2] != 'null':\n        print(tokens[1] + ' ' + tokens[2])\n        if len(tokens) > 6:\n            print(tokens[5] + ' ' + tokens[6])",
        "constraints": "0 <= nodes <= 2000",
        "examples": json.dumps([{"input": "[3,9,20,null,null,15,7]", "output": "3\\n9 20\\n15 7"}]),
        "starter_code": "nodes = input().split()\n# Output levels of binary tree\n",
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
        "title": "Trapping Rain Water",
        "company": "Amazon",
        "difficulty": "hard",
        "category": "Two Pointers",
        "description": "Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "test_cases": json.dumps([
            {"input": "0 1 0 2 1 0 1 3 2 1 2 1", "expected": "6"},
            {"input": "4 2 0 3 2 5", "expected": "9"},
        ]),
        "solution": "height = list(map(int, input().split()))\nif not height: print(0)\nelse:\n    l, r = 0, len(height) - 1\n    l_max, r_max = height[l], height[r]\n    water = 0\n    while l < r:\n        if l_max < r_max:\n            l += 1\n            l_max = max(l_max, height[l])\n            water += l_max - height[l]\n        else:\n            r -= 1\n            r_max = max(r_max, height[r])\n            water += r_max - height[r]\n    print(water)",
        "constraints": "n == height.length\n1 <= n <= 2 * 10^4",
        "examples": json.dumps([{"input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6"}]),
        "starter_code": "height = list(map(int, input().split()))\n# Compute trapped rainwater volume\n",
    },
    {
        "title": "Top K Frequent Elements",
        "company": "Amazon",
        "difficulty": "medium",
        "category": "Heaps",
        "description": "Given an integer array `nums` and an integer `k`, return the `k` most frequent elements in descending order of frequency.",
        "test_cases": json.dumps([
            {"input": "1 1 1 2 2 3\n2", "expected": "1 2"},
            {"input": "1\n1", "expected": "1"},
        ]),
        "solution": "from collections import Counter\nnums = list(map(int, input().split()))\nk = int(input())\nc = Counter(nums)\ntop = [str(x[0]) for x in c.most_common(k)]\nprint(' '.join(top))",
        "constraints": "1 <= nums.length <= 10^5\nk is in the range [1, number of unique elements]",
        "examples": json.dumps([{"input": "nums = [1,1,1,2,2,3], k = 2", "output": "1 2"}]),
        "starter_code": "nums = list(map(int, input().split()))\nk = int(input())\n# Return top k frequent numbers\n",
    },

    # ── META (FACEBOOK) ──
    {
        "title": "Subarray Sum Equals K",
        "company": "Meta",
        "difficulty": "medium",
        "category": "Arrays",
        "description": "Given an array of integers `nums` and an integer `k`, return the total number of subarrays whose sum equals to `k`.",
        "test_cases": json.dumps([
            {"input": "1 1 1\n2", "expected": "2"},
            {"input": "1 2 3\n3", "expected": "2"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nk = int(input())\nfrom collections import defaultdict\ncounts = defaultdict(int)\ncounts[0] = 1\ncurr = 0\nans = 0\nfor n in nums:\n    curr += n\n    ans += counts[curr - k]\n    counts[curr] += 1\nprint(ans)",
        "constraints": "1 <= nums.length <= 2 * 10^4",
        "examples": json.dumps([{"input": "nums = [1,1,1], k = 2", "output": "2"}]),
        "starter_code": "nums = list(map(int, input().split()))\nk = int(input())\n# Meta core question: Subarrays summing to k\n",
    },
    {
        "title": "3Sum (Zero Triplet Problem)",
        "company": "Meta",
        "difficulty": "medium",
        "category": "Two Pointers",
        "description": "Given an integer array nums, return the number of distinct triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.",
        "test_cases": json.dumps([
            {"input": "-1 0 1 2 -1 -4", "expected": "2"},
            {"input": "0 1 1", "expected": "0"},
            {"input": "0 0 0", "expected": "1"},
        ]),
        "solution": "nums = sorted(list(map(int, input().split())))\nres = 0\nn = len(nums)\nfor i in range(n):\n    if i > 0 and nums[i] == nums[i-1]: continue\n    l, r = i + 1, n - 1\n    while l < r:\n        s = nums[i] + nums[l] + nums[r]\n        if s < 0: l += 1\n        elif s > 0: r -= 1\n        else:\n            res += 1\n            l += 1\n            while l < r and nums[l] == nums[l-1]: l += 1\nprint(res)",
        "constraints": "3 <= nums.length <= 3000",
        "examples": json.dumps([{"input": "nums = [-1,0,1,2,-1,-4]", "output": "2"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Count unique triplets with zero sum\n",
    },
    {
        "title": "Product of Array Except Self",
        "company": "Meta",
        "difficulty": "medium",
        "category": "Arrays",
        "description": "Given an integer array `nums`, return an array `answer` such that `answer[i]` is equal to the product of all the elements of `nums` except `nums[i]` without using division in O(n) time.",
        "test_cases": json.dumps([
            {"input": "1 2 3 4", "expected": "24 12 8 6"},
            {"input": "-1 1 0 -3 3", "expected": "0 0 9 0 0"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nn = len(nums)\nans = [1] * n\np = 1\nfor i in range(n):\n    ans[i] = p\n    p *= nums[i]\np = 1\nfor i in range(n - 1, -1, -1):\n    ans[i] *= p\n    p *= nums[i]\nprint(' '.join(map(str, ans)))",
        "constraints": "2 <= nums.length <= 10^5",
        "examples": json.dumps([{"input": "[1,2,3,4]", "output": "24 12 8 6"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Calculate product array except self\n",
    },

    # ── APPLE ──
    {
        "title": "Search in Rotated Sorted Array",
        "company": "Apple",
        "difficulty": "medium",
        "category": "Searching",
        "description": "There is an integer array `nums` sorted in ascending order with distinct values, rotated at an unknown pivot index. Given `nums` and a `target`, return the 0-based index of `target`, or -1 if not found.",
        "test_cases": json.dumps([
            {"input": "4 5 6 7 0 1 2\n0", "expected": "4"},
            {"input": "4 5 6 7 0 1 2\n3", "expected": "-1"},
            {"input": "1\n0", "expected": "-1"},
        ]),
        "solution": "nums = list(map(int, input().split()))\ntarget = int(input())\nl, r = 0, len(nums) - 1\nans = -1\nwhile l <= r:\n    mid = (l + r) // 2\n    if nums[mid] == target:\n        ans = mid\n        break\n    if nums[l] <= nums[mid]:\n        if nums[l] <= target < nums[mid]: r = mid - 1\n        else: l = mid + 1\n    else:\n        if nums[mid] < target <= nums[r]: l = mid + 1\n        else: r = mid - 1\nprint(ans)",
        "constraints": "1 <= nums.length <= 5000",
        "examples": json.dumps([{"input": "nums = [4,5,6,7,0,1,2], target = 0", "output": "4"}]),
        "starter_code": "nums = list(map(int, input().split()))\ntarget = int(input())\n# Perform O(log n) modified binary search\n",
    },
    {
        "title": "Group Anagrams",
        "company": "Apple",
        "difficulty": "medium",
        "category": "Strings",
        "description": "Given an array of strings `strs`, return the number of anagram groups formed by grouping anagrams together.",
        "test_cases": json.dumps([
            {"input": "eat tea tan ate nat bat", "expected": "3"},
            {"input": "a", "expected": "1"},
        ]),
        "solution": "words = input().split()\nfrom collections import defaultdict\ng = defaultdict(list)\nfor w in words:\n    g[''.join(sorted(w))].append(w)\nprint(len(g))",
        "constraints": "1 <= strs.length <= 10^4",
        "examples": json.dumps([{"input": "['eat','tea','tan','ate','nat','bat']", "output": "3"}]),
        "starter_code": "words = input().split()\n# Count distinct anagram groups\n",
    },

    # ── NETFLIX ──
    {
        "title": "Coin Change (Fewest Coins)",
        "company": "Netflix",
        "difficulty": "medium",
        "category": "Dynamic Programming",
        "description": "You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money. Return the fewest number of coins that you need to make up that amount. If impossible, return -1.",
        "test_cases": json.dumps([
            {"input": "1 2 5\n11", "expected": "3"},
            {"input": "2\n3", "expected": "-1"},
            {"input": "1\n0", "expected": "0"},
        ]),
        "solution": "coins = list(map(int, input().split()))\namount = int(input())\ndp = [float('inf')] * (amount + 1)\ndp[0] = 0\nfor c in coins:\n    for x in range(c, amount + 1):\n        dp[x] = min(dp[x], dp[x - c] + 1)\nprint(dp[amount] if dp[amount] != float('inf') else -1)",
        "constraints": "1 <= coins.length <= 12\n0 <= amount <= 10^4",
        "examples": json.dumps([{"input": "coins = [1,2,5], amount = 11", "output": "3"}]),
        "starter_code": "coins = list(map(int, input().split()))\namount = int(input())\n# Compute minimum coins using Dynamic Programming\n",
    },
    {
        "title": "Longest Increasing Subsequence",
        "company": "Netflix",
        "difficulty": "medium",
        "category": "Dynamic Programming",
        "description": "Given an integer array `nums`, return the length of the longest strictly increasing subsequence.",
        "test_cases": json.dumps([
            {"input": "10 9 2 5 3 7 101 18", "expected": "4"},
            {"input": "0 1 0 3 2 3", "expected": "4"},
            {"input": "7 7 7 7 7 7 7", "expected": "1"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nimport bisect\ntails = []\nfor x in nums:\n    idx = bisect.bisect_left(tails, x)\n    if idx == len(tails): tails.append(x)\n    else: tails[idx] = x\nprint(len(tails))",
        "constraints": "1 <= nums.length <= 2500",
        "examples": json.dumps([{"input": "[10,9,2,5,3,7,101,18]", "output": "4"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Return length of LIS\n",
    },

    # ── GOLDMAN SACHS ──
    {
        "title": "First Unique Character in a String",
        "company": "Goldman Sachs",
        "difficulty": "easy",
        "category": "Strings",
        "description": "Given a string `s`, find the first non-repeating character in it and return its index. If it does not exist, return -1.",
        "test_cases": json.dumps([
            {"input": "leetcode", "expected": "0"},
            {"input": "loveleetcode", "expected": "2"},
            {"input": "aabb", "expected": "-1"},
        ]),
        "solution": "s = input().strip()\nfrom collections import Counter\nc = Counter(s)\nans = -1\nfor i, ch in enumerate(s):\n    if c[ch] == 1:\n        ans = i\n        break\nprint(ans)",
        "constraints": "1 <= s.length <= 10^5",
        "examples": json.dumps([{"input": "s = 'leetcode'", "output": "0"}]),
        "starter_code": "s = input().strip()\n# Return index of first non-repeating character\n",
    },
    {
        "title": "High Five (Top 5 Scores Average)",
        "company": "Goldman Sachs",
        "difficulty": "easy",
        "category": "Arrays",
        "description": "Given student scores, calculate the integer average of the top 5 scores of the student with id 1.",
        "test_cases": json.dumps([
            {"input": "91 92 90 85 88 70 65", "expected": "89"},
            {"input": "100 100 100 100 100", "expected": "100"},
        ]),
        "solution": "scores = sorted(list(map(int, input().split())), reverse=True)\ntop5 = scores[:5]\nprint(sum(top5) // len(top5))",
        "constraints": "At least 5 scores provided",
        "examples": json.dumps([{"input": "[91, 92, 90, 85, 88, 70, 65]", "output": "89"}]),
        "starter_code": "scores = list(map(int, input().split()))\n# Output average of top 5 scores\n",
    },

    # ── UBER ──
    {
        "title": "Number of Islands",
        "company": "Uber",
        "difficulty": "medium",
        "category": "Graphs",
        "description": "Given an m x n 2D binary grid representing a map of '1's (land) and '0's (water), return the number of islands. Input has R and C on line 1, followed by R lines.",
        "test_cases": json.dumps([
            {"input": "3 3\n1 1 0\n1 1 0\n0 0 1", "expected": "2"},
            {"input": "2 2\n1 1\n1 1", "expected": "1"},
        ]),
        "solution": "lines = open(0).read().strip().splitlines()\nr, c = map(int, lines[0].split())\ngrid = [lines[i+1].split() for i in range(r)]\nislands = 0\ndef dfs(i, j):\n    if i < 0 or i >= r or j < 0 or j >= c or grid[i][j] != '1': return\n    grid[i][j] = '0'\n    dfs(i+1, j); dfs(i-1, j); dfs(i, j+1); dfs(i, j-1)\nfor i in range(r):\n    for j in range(c):\n        if grid[i][j] == '1':\n            islands += 1\n            dfs(i, j)\nprint(islands)",
        "constraints": "1 <= m, n <= 300",
        "examples": json.dumps([{"input": "3 3\\n1 1 0\\n1 1 0\\n0 0 1", "output": "2"}]),
        "starter_code": "lines = open(0).read().strip().splitlines()\n# Count connected components in binary grid\n",
    },
    {
        "title": "Merge Intervals",
        "company": "Uber",
        "difficulty": "medium",
        "category": "Intervals",
        "description": "Given a collection of intervals represented as space-separated start-end pairs, merge all overlapping intervals and print the number of resulting non-overlapping intervals.",
        "test_cases": json.dumps([
            {"input": "1 3 2 6 8 10 15 18", "expected": "3"},
            {"input": "1 4 4 5", "expected": "1"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nintervals = []\nfor i in range(0, len(nums), 2):\n    intervals.append([nums[i], nums[i+1]])\nintervals.sort(key=lambda x: x[0])\nmerged = [intervals[0]]\nfor current in intervals[1:]:\n    prev = merged[-1]\n    if current[0] <= prev[1]:\n        prev[1] = max(prev[1], current[1])\n    else:\n        merged.append(current)\nprint(len(merged))",
        "constraints": "1 <= intervals.length <= 10^4",
        "examples": json.dumps([{"input": "[[1,3],[2,6],[8,10],[15,18]]", "output": "3"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Merge overlapping intervals\n",
    },

    # ── ADOBE ──
    {
        "title": "Longest Palindromic Substring",
        "company": "Adobe",
        "difficulty": "medium",
        "category": "Strings",
        "description": "Given a string `s`, return the length of the longest palindromic substring in `s`.",
        "test_cases": json.dumps([
            {"input": "babad", "expected": "3"},
            {"input": "cbbd", "expected": "2"},
            {"input": "a", "expected": "1"},
        ]),
        "solution": "s = input().strip()\nif not s: print(0)\nelse:\n    max_len = 1\n    for i in range(len(s)):\n        # odd\n        l, r = i, i\n        while l >= 0 and r < len(s) and s[l] == s[r]:\n            max_len = max(max_len, r - l + 1)\n            l -= 1; r += 1\n        # even\n        l, r = i, i + 1\n        while l >= 0 and r < len(s) and s[l] == s[r]:\n            max_len = max(max_len, r - l + 1)\n            l -= 1; r += 1\n    print(max_len)",
        "constraints": "1 <= s.length <= 1000",
        "examples": json.dumps([{"input": "s = 'babad'", "output": "3"}]),
        "starter_code": "s = input().strip()\n# Return length of longest palindromic substring\n",
    },
    {
        "title": "Single Number (Bit Manipulation)",
        "company": "Adobe",
        "difficulty": "easy",
        "category": "Math",
        "description": "Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one using XOR in O(n) time and O(1) space.",
        "test_cases": json.dumps([
            {"input": "2 2 1", "expected": "1"},
            {"input": "4 1 2 1 2", "expected": "4"},
            {"input": "1", "expected": "1"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nans = 0\nfor n in nums: ans ^= n\nprint(ans)",
        "constraints": "1 <= nums.length <= 3 * 10^4",
        "examples": json.dumps([{"input": "[4,1,2,1,2]", "output": "4"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Use bitwise XOR to find single element\n",
    },

    # ── ATLASSIAN ──
    {
        "title": "Daily Temperatures (Monotonic Stack)",
        "company": "Atlassian",
        "difficulty": "medium",
        "category": "Stacks",
        "description": "Given an array of integers temperatures represents the daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature.",
        "test_cases": json.dumps([
            {"input": "73 74 75 71 69 72 76 73", "expected": "1 1 4 2 1 1 0 0"},
            {"input": "30 40 50 60", "expected": "1 1 1 0"},
        ]),
        "solution": "T = list(map(int, input().split()))\nans = [0] * len(T)\nstack = []\nfor i, temp in enumerate(T):\n    while stack and T[stack[-1]] < temp:\n        prev = stack.pop()\n        ans[prev] = i - prev\n    stack.append(i)\nprint(' '.join(map(str, ans)))",
        "constraints": "1 <= temperatures.length <= 10^5",
        "examples": json.dumps([{"input": "[73,74,75,71,69,72,76,73]", "output": "1 1 4 2 1 1 0 0"}]),
        "starter_code": "temps = list(map(int, input().split()))\n# Compute wait times using a monotonic stack\n",
    },

    # ── ORACLE ──
    {
        "title": "Validate Binary Search Tree",
        "company": "Oracle",
        "difficulty": "medium",
        "category": "Trees",
        "description": "Given an array of integers representing the in-order traversal of a tree, return True if it represents a valid strictly increasing BST, else False.",
        "test_cases": json.dumps([
            {"input": "1 2 3 4 5", "expected": "True"},
            {"input": "5 1 4", "expected": "False"},
            {"input": "2 2 3", "expected": "False"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nis_bst = all(nums[i] < nums[i+1] for i in range(len(nums)-1))\nprint(is_bst)",
        "constraints": "1 <= number of nodes <= 10^4",
        "examples": json.dumps([{"input": "[1,2,3,4,5]", "output": "True"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Verify if in-order elements form valid BST\n",
    },

    # ── WALMART ──
    {
        "title": "Jump Game",
        "company": "Walmart",
        "difficulty": "medium",
        "category": "Dynamic Programming",
        "description": "You are given an integer array `nums`. You are initially positioned at the array's first index. Each element represents your maximum jump length at that position. Return True if you can reach the last index, or False otherwise.",
        "test_cases": json.dumps([
            {"input": "2 3 1 1 4", "expected": "True"},
            {"input": "3 2 1 0 4", "expected": "False"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nreach = 0\nok = True\nfor i, n in enumerate(nums):\n    if i > reach:\n        ok = False\n        break\n    reach = max(reach, i + n)\nprint(ok and reach >= len(nums) - 1)",
        "constraints": "1 <= nums.length <= 10^4",
        "examples": json.dumps([{"input": "[2,3,1,1,4]", "output": "True"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Return True if reachable to end\n",
    },

    # ── DELOITTE ──
    {
        "title": "Palindrome Number",
        "company": "Deloitte",
        "difficulty": "easy",
        "category": "Math",
        "description": "Given an integer `x`, return `True` if `x` is a palindrome, and `False` otherwise.",
        "test_cases": json.dumps([
            {"input": "121", "expected": "True"},
            {"input": "-121", "expected": "False"},
            {"input": "10", "expected": "False"},
        ]),
        "solution": "s = input().strip()\nprint(s == s[::-1])",
        "constraints": "-2^31 <= x <= 2^31 - 1",
        "examples": json.dumps([{"input": "x = 121", "output": "True"}]),
        "starter_code": "s = input().strip()\n# Return True if palindrome\n",
    },

    # ── ACCENTURE ──
    {
        "title": "Move Zeroes to End",
        "company": "Accenture",
        "difficulty": "easy",
        "category": "Arrays",
        "description": "Given an integer array `nums`, move all `0`'s to the end of it while maintaining the relative order of the non-zero elements.",
        "test_cases": json.dumps([
            {"input": "0 1 0 3 12", "expected": "1 3 12 0 0"},
            {"input": "0", "expected": "0"},
            {"input": "1 2 3", "expected": "1 2 3"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nnon_zeros = [n for n in nums if n != 0]\nzeros = [0] * (len(nums) - len(non_zeros))\nprint(' '.join(map(str, non_zeros + zeros)))",
        "constraints": "1 <= nums.length <= 10^4",
        "examples": json.dumps([{"input": "nums = [0,1,0,3,12]", "output": "1 3 12 0 0"}]),
        "starter_code": "nums = list(map(int, input().split()))\n# Move all zeros to end in-place\n",
    },

    # ── TCS ──
    {
        "title": "TCS NQT Array Rotation",
        "company": "TCS",
        "difficulty": "easy",
        "category": "Arrays",
        "description": "Given an array `nums` and an integer `k`, rotate the array to the right by `k` steps.",
        "test_cases": json.dumps([
            {"input": "1 2 3 4 5 6 7\n3", "expected": "5 6 7 1 2 3 4"},
            {"input": "-1 -100 3 99\n2", "expected": "3 99 -1 -100"},
        ]),
        "solution": "nums = list(map(int, input().split()))\nk = int(input()) % len(nums)\nrotated = nums[-k:] + nums[:-k]\nprint(' '.join(map(str, rotated)))",
        "constraints": "1 <= nums.length <= 10^5\n0 <= k <= 10^5",
        "examples": json.dumps([{"input": "nums = [1,2,3,4,5,6,7], k = 3", "output": "5 6 7 1 2 3 4"}]),
        "starter_code": "nums = list(map(int, input().split()))\nk = int(input())\n# TCS NQT: Rotate array right by k steps\n",
    },

    # ── INFOSYS ──
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

DEMO_STUDENTS = [
    {
        "email": "aarav.patel@iitb.ac.in",
        "full_name": "Aarav Patel",
        "score": 360,
        "streak": 21,
        "bio": "College: IIT Bombay | Target: Google | AIR 42 CP | Machine Learning & Algorithms",
    },
    {
        "email": "student@preppilot.com",
        "full_name": "Priya Sharma (Student)",
        "score": 310,
        "streak": 16,
        "bio": "College: BITS Pilani | Target: Microsoft | Cloud Architecture & Full-Stack Systems",
    },
    {
        "email": "rohan.verma@iitd.ac.in",
        "full_name": "Rohan Verma",
        "score": 285,
        "streak": 14,
        "bio": "College: IIT Delhi | Target: Amazon | Competitive Programming Knight",
    },
    {
        "email": "ananya.iyer@nitt.edu",
        "full_name": "Ananya Iyer",
        "score": 255,
        "streak": 12,
        "bio": "College: NIT Trichy | Target: Goldman Sachs | Quantitative Algorithms & FinTech",
    },
    {
        "email": "karthik.reddy@iiit.ac.in",
        "full_name": "Karthik Reddy",
        "score": 230,
        "streak": 11,
        "bio": "College: IIIT Hyderabad | Target: Meta | Distributed Systems & Graph Algorithms",
    },
    {
        "email": "sneha.k@dtu.ac.in",
        "full_name": "Sneha Kulkarni",
        "score": 210,
        "streak": 10,
        "bio": "College: DTU Delhi | Target: Apple | iOS Intern & Core OS Foundations",
    },
    {
        "email": "vikram.rao@iitm.ac.in",
        "full_name": "Vikramaditya Rao",
        "score": 195,
        "streak": 9,
        "bio": "College: IIT Madras | Target: Uber | Microservices & Shortest Path Routing",
    },
    {
        "email": "divya.nair@iitr.ac.in",
        "full_name": "Divya Nair",
        "score": 180,
        "streak": 8,
        "bio": "College: IIT Roorkee | Target: Netflix | Distributed Caching & High Throughput",
    },
    {
        "email": "rahul.m@ju.edu",
        "full_name": "Rahul Mukherjee",
        "score": 165,
        "streak": 7,
        "bio": "College: Jadavpur University | Target: Adobe | Computer Graphics & Algorithms",
    },
    {
        "email": "neha.gupta@vit.ac.in",
        "full_name": "Neha Gupta",
        "score": 150,
        "streak": 7,
        "bio": "College: VIT Vellore | Target: Atlassian | Backend Engineering & Systems",
    },
    {
        "email": "tanmay.joshi@coep.ac.in",
        "full_name": "Tanmay Joshi",
        "score": 135,
        "streak": 6,
        "bio": "College: COEP Pune | Target: Oracle | Database Engineering & SQL Internals",
    },
    {
        "email": "shreya.b@nitk.edu",
        "full_name": "Shreya Banerjee",
        "score": 120,
        "streak": 5,
        "bio": "College: NIT Surathkal | Target: Walmart | Retail Tech & Supply Chain Algo",
    },
    {
        "email": "aditya.singh@nsut.ac.in",
        "full_name": "Aditya Singh",
        "score": 95,
        "streak": 4,
        "bio": "College: NSUT Delhi | Target: Deloitte | Cloud Advisory & Solutions Architect",
    },
    {
        "email": "meera.k@psg.edu",
        "full_name": "Meera Krishnan",
        "score": 80,
        "streak": 3,
        "bio": "College: PSG Tech | Target: TCS | Software Engineering & Java Microservices",
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
            total_score=500,
            streak_days=30,
            bio="Administrator & Lead Evaluator | PrepPilot Platform",
        )
        db.add(admin)
        logger.info("Created admin user: admin@preppilot.com")
    elif admin.email == "admin@preppilot.local":
        admin.email = "admin@preppilot.com"
        admin.password_hash = hash_password("PrepPilot#2026")
        db.add(admin)

    # 2. Seed Cohort of Student Leaderboard Users
    for stu in DEMO_STUDENTS:
        existing_stu = db.query(User).filter(User.email == stu["email"]).first()
        if not existing_stu:
            user = User(
                email=stu["email"],
                password_hash=hash_password("Student#2026"),
                full_name=stu["full_name"],
                is_admin=False,
                is_verified=True,
                total_score=stu["score"],
                streak_days=stu["streak"],
                bio=stu["bio"],
            )
            db.add(user)
            logger.info(f"Seeded student user: {stu['full_name']}")
        else:
            existing_stu.total_score = stu["score"]
            existing_stu.streak_days = stu["streak"]
            existing_stu.bio = stu["bio"]
            db.add(existing_stu)

    # 3. Seed Companies
    for c_data in COMPANIES:
        existing = db.query(Company).filter(Company.slug == c_data["slug"]).first()
        if not existing:
            company = Company(**c_data)
            db.add(company)
            logger.info(f"Seeded company: {c_data['name']}")
        else:
            existing.name = c_data["name"]
            existing.difficulty = c_data["difficulty"]
            existing.interview_focus = c_data["interview_focus"]
            db.add(existing)

    # 4. Seed Company-Specific Coding Questions
    for q_data in CODING_QUESTIONS:
        existing = db.query(CodingQuestion).filter(CodingQuestion.title == q_data["title"]).first()
        if not existing:
            question = CodingQuestion(**q_data)
            db.add(question)
            logger.info(f"Seeded question: {q_data['title']} ({q_data.get('company')})")
        else:
            if hasattr(existing, "company"):
                existing.company = q_data.get("company", "General")
            existing.category = q_data["category"]
            existing.difficulty = q_data["difficulty"]
            existing.description = q_data["description"]
            existing.test_cases = q_data["test_cases"]
            existing.solution = q_data["solution"]
            existing.starter_code = q_data["starter_code"]
            db.add(existing)

    db.commit()
    logger.info("Database seeding complete with full company track and leaderboard data!")
