"""Seed demo data: companies, coding questions, and admin user."""

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
        "description": "Google is a global technology leader specializing in Internet-related services and products including search, cloud computing, advertising, and AI.",
        "industry": "Technology",
        "difficulty": "hard",
        "interview_focus": '["DSA","System Design","Problem Solving","Googleyness"]',
    },
    {
        "name": "Microsoft",
        "slug": "microsoft",
        "logo_url": "https://logo.clearbit.com/microsoft.com",
        "description": "Microsoft is a multinational technology corporation producing computer software, consumer electronics, and cloud services.",
        "industry": "Technology",
        "difficulty": "hard",
        "interview_focus": '["DSA","System Design","OOP","Behavioral"]',
    },
    {
        "name": "Amazon",
        "slug": "amazon",
        "logo_url": "https://logo.clearbit.com/amazon.com",
        "description": "Amazon is a multinational technology company focusing on e-commerce, cloud computing (AWS), digital streaming, and AI.",
        "industry": "Technology / E-commerce",
        "difficulty": "hard",
        "interview_focus": '["Leadership Principles","DSA","System Design","Behavioral"]',
    },
    {
        "name": "Goldman Sachs",
        "slug": "goldman-sachs",
        "logo_url": "https://logo.clearbit.com/goldmansachs.com",
        "description": "Goldman Sachs is a leading global investment banking, securities, and investment management firm.",
        "industry": "Finance",
        "difficulty": "hard",
        "interview_focus": '["DSA","Quantitative","Finance","Problem Solving"]',
    },
    {
        "name": "Deloitte",
        "slug": "deloitte",
        "logo_url": "https://logo.clearbit.com/deloitte.com",
        "description": "Deloitte is one of the Big Four professional services networks, offering audit, tax, consulting, and advisory services.",
        "industry": "Consulting",
        "difficulty": "medium",
        "interview_focus": '["Case Studies","Behavioral","Technical","Aptitude"]',
    },
    {
        "name": "Accenture",
        "slug": "accenture",
        "logo_url": "https://logo.clearbit.com/accenture.com",
        "description": "Accenture is a global professional services company with leading capabilities in digital, cloud, and security.",
        "industry": "Consulting / IT",
        "difficulty": "medium",
        "interview_focus": '["Technical","Behavioral","Aptitude","Communication"]',
    },
    {
        "name": "TCS",
        "slug": "tcs",
        "logo_url": "https://logo.clearbit.com/tcs.com",
        "description": "Tata Consultancy Services is an Indian multinational IT services and consulting company.",
        "industry": "IT Services",
        "difficulty": "easy",
        "interview_focus": '["Aptitude","Technical Basics","Coding","HR"]',
    },
    {
        "name": "Infosys",
        "slug": "infosys",
        "logo_url": "https://logo.clearbit.com/infosys.com",
        "description": "Infosys is a global leader in next-generation digital services and consulting.",
        "industry": "IT Services",
        "difficulty": "easy",
        "interview_focus": '["Aptitude","Technical Basics","Coding","Behavioral"]',
    },
]

CODING_QUESTIONS = [
    {
        "title": "Two Sum",
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nReturn the answer in any order.",
        "difficulty": "easy",
        "category": "arrays",
        "test_cases": json.dumps([
            {"input": "2 7 11 15\\n9", "expected": "0 1"},
            {"input": "3 2 4\\n6", "expected": "1 2"},
            {"input": "3 3\\n6", "expected": "0 1"},
        ]),
        "solution": "def two_sum(nums, target):\\n    seen = {}\\n    for i, n in enumerate(nums):\\n        comp = target - n\\n        if comp in seen:\\n            return [seen[comp], i]\\n        seen[n] = i\\n\\nnums = list(map(int, input().split()))\\ntarget = int(input())\\nresult = two_sum(nums, target)\\nprint(*result)",
        "constraints": "2 <= nums.length <= 10^4\\n-10^9 <= nums[i] <= 10^9\\n-10^9 <= target <= 10^9",
        "examples": json.dumps([
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."},
        ]),
        "starter_code": "# Read input and solve Two Sum\\nnums = list(map(int, input().split()))\\ntarget = int(input())\\n\\n# Your code here\\n",
    },
    {
        "title": "Reverse String",
        "description": "Write a function that reverses a string. The input string is given as an array of characters.\n\nDo this in-place with O(1) extra memory.",
        "difficulty": "easy",
        "category": "strings",
        "test_cases": json.dumps([
            {"input": "hello", "expected": "olleh"},
            {"input": "Hannah", "expected": "hannaH"},
            {"input": "a", "expected": "a"},
        ]),
        "solution": "s = input()\\nprint(s[::-1])",
        "constraints": "1 <= s.length <= 10^5",
        "examples": json.dumps([
            {"input": "hello", "output": "olleh"},
        ]),
        "starter_code": "s = input()\\n# Reverse the string and print\\n",
    },
    {
        "title": "Palindrome Check",
        "description": "Given a string `s`, determine if it is a palindrome, considering only alphanumeric characters and ignoring cases.\n\nPrint `True` if it is a palindrome, `False` otherwise.",
        "difficulty": "easy",
        "category": "strings",
        "test_cases": json.dumps([
            {"input": "A man, a plan, a canal: Panama", "expected": "True"},
            {"input": "race a car", "expected": "False"},
            {"input": " ", "expected": "True"},
        ]),
        "solution": "s = input()\\nclean = ''.join(c.lower() for c in s if c.isalnum())\\nprint(clean == clean[::-1])",
        "constraints": "1 <= s.length <= 2 * 10^5",
        "examples": json.dumps([
            {"input": "A man, a plan, a canal: Panama", "output": "True"},
        ]),
        "starter_code": "s = input()\\n# Check if palindrome\\n",
    },
    {
        "title": "FizzBuzz",
        "description": "Given an integer `n`, print each number from 1 to n on a new line. For multiples of 3, print 'Fizz'; for multiples of 5, print 'Buzz'; for multiples of both 3 and 5, print 'FizzBuzz'.",
        "difficulty": "easy",
        "category": "basics",
        "test_cases": json.dumps([
            {"input": "5", "expected": "1\\n2\\nFizz\\n4\\nBuzz"},
            {"input": "15", "expected": "1\\n2\\nFizz\\n4\\nBuzz\\nFizz\\n7\\n8\\nFizz\\nBuzz\\n11\\nFizz\\n13\\n14\\nFizzBuzz"},
        ]),
        "solution": "n = int(input())\\nfor i in range(1, n+1):\\n    if i % 15 == 0: print('FizzBuzz')\\n    elif i % 3 == 0: print('Fizz')\\n    elif i % 5 == 0: print('Buzz')\\n    else: print(i)",
        "constraints": "1 <= n <= 10^4",
        "examples": json.dumps([
            {"input": "3", "output": "1\\n2\\nFizz"},
        ]),
        "starter_code": "n = int(input())\\n# Print FizzBuzz sequence\\n",
    },
    {
        "title": "Maximum Subarray (Kadane's)",
        "description": "Given an integer array `nums`, find the subarray with the largest sum, and return its sum.",
        "difficulty": "medium",
        "category": "arrays",
        "test_cases": json.dumps([
            {"input": "-2 1 -3 4 -1 2 1 -5 4", "expected": "6"},
            {"input": "1", "expected": "1"},
            {"input": "5 4 -1 7 8", "expected": "23"},
        ]),
        "solution": "nums = list(map(int, input().split()))\\nmax_sum = curr = nums[0]\\nfor n in nums[1:]:\\n    curr = max(n, curr + n)\\n    max_sum = max(max_sum, curr)\\nprint(max_sum)",
        "constraints": "1 <= nums.length <= 10^5\\n-10^4 <= nums[i] <= 10^4",
        "examples": json.dumps([
            {"input": "[-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explanation": "The subarray [4,-1,2,1] has the largest sum 6."},
        ]),
        "starter_code": "nums = list(map(int, input().split()))\\n# Find maximum subarray sum\\n",
    },
    {
        "title": "Valid Parentheses",
        "description": "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.\n\nPrint `True` or `False`.",
        "difficulty": "easy",
        "category": "stacks",
        "test_cases": json.dumps([
            {"input": "()", "expected": "True"},
            {"input": "()[]{}", "expected": "True"},
            {"input": "(]", "expected": "False"},
            {"input": "([)]", "expected": "False"},
        ]),
        "solution": "s = input()\\nstack = []\\nmapping = {')':'(', '}':'{', ']':'['}\\nfor c in s:\\n    if c in mapping:\\n        if not stack or stack[-1] != mapping[c]:\\n            print(False)\\n            exit()\\n        stack.pop()\\n    else:\\n        stack.append(c)\\nprint(len(stack) == 0)",
        "constraints": "1 <= s.length <= 10^4",
        "examples": json.dumps([{"input": "()[]{}", "output": "True"}]),
        "starter_code": "s = input()\\n# Check if parentheses are valid\\n",
    },
    {
        "title": "Linked List Cycle Detection",
        "description": "Given a linked list represented as space-separated node values followed by a position (0-indexed) where the tail connects to, determine if the linked list has a cycle.\n\nPrint `True` if there is a cycle, `False` otherwise. Position -1 means no cycle.",
        "difficulty": "medium",
        "category": "linked_lists",
        "test_cases": json.dumps([
            {"input": "3 2 0 -4\\n1", "expected": "True"},
            {"input": "1 2\\n0", "expected": "True"},
            {"input": "1\\n-1", "expected": "False"},
        ]),
        "solution": "vals = list(map(int, input().split()))\\npos = int(input())\\nprint(pos >= 0)",
        "constraints": "0 <= number of nodes <= 10^4",
        "examples": json.dumps([{"input": "3 2 0 -4, pos = 1", "output": "True"}]),
        "starter_code": "vals = list(map(int, input().split()))\\npos = int(input())\\n# Detect cycle\\n",
    },
    {
        "title": "Binary Search",
        "description": "Given a sorted array of integers `nums` and a `target` value, implement binary search.\n\nPrint the index if `target` is found, otherwise print -1.",
        "difficulty": "easy",
        "category": "searching",
        "test_cases": json.dumps([
            {"input": "-1 0 3 5 9 12\\n9", "expected": "4"},
            {"input": "-1 0 3 5 9 12\\n2", "expected": "-1"},
            {"input": "5\\n5", "expected": "0"},
        ]),
        "solution": "nums = list(map(int, input().split()))\\ntarget = int(input())\\nlo, hi = 0, len(nums) - 1\\nwhile lo <= hi:\\n    mid = (lo + hi) // 2\\n    if nums[mid] == target: print(mid); exit()\\n    elif nums[mid] < target: lo = mid + 1\\n    else: hi = mid - 1\\nprint(-1)",
        "constraints": "1 <= nums.length <= 10^4\\n-10^4 <= nums[i], target <= 10^4",
        "examples": json.dumps([{"input": "[-1,0,3,5,9,12], target=9", "output": "4"}]),
        "starter_code": "nums = list(map(int, input().split()))\\ntarget = int(input())\\n# Implement binary search\\n",
    },
    {
        "title": "Merge Sort",
        "description": "Given an array of integers, sort the array using merge sort and print the sorted array as space-separated values.",
        "difficulty": "medium",
        "category": "sorting",
        "test_cases": json.dumps([
            {"input": "5 2 3 1", "expected": "1 2 3 5"},
            {"input": "5 1 1 2 0 0", "expected": "0 0 1 1 2 5"},
            {"input": "1", "expected": "1"},
        ]),
        "solution": "def merge_sort(arr):\\n    if len(arr) <= 1: return arr\\n    mid = len(arr) // 2\\n    left = merge_sort(arr[:mid])\\n    right = merge_sort(arr[mid:])\\n    result = []\\n    i = j = 0\\n    while i < len(left) and j < len(right):\\n        if left[i] <= right[j]: result.append(left[i]); i += 1\\n        else: result.append(right[j]); j += 1\\n    result.extend(left[i:])\\n    result.extend(right[j:])\\n    return result\\n\\narr = list(map(int, input().split()))\\nprint(*merge_sort(arr))",
        "constraints": "1 <= arr.length <= 5 * 10^4",
        "examples": json.dumps([{"input": "[5,2,3,1]", "output": "[1,2,3,5]"}]),
        "starter_code": "arr = list(map(int, input().split()))\\n# Implement merge sort\\n",
    },
    {
        "title": "Longest Common Subsequence",
        "description": "Given two strings `text1` and `text2`, return the length of their longest common subsequence.\n\nA subsequence is a sequence that can be derived from another sequence by deleting some or no elements without changing the order of the remaining elements.",
        "difficulty": "hard",
        "category": "dynamic_programming",
        "test_cases": json.dumps([
            {"input": "abcde\\nace", "expected": "3"},
            {"input": "abc\\nabc", "expected": "3"},
            {"input": "abc\\ndef", "expected": "0"},
        ]),
        "solution": "t1 = input()\\nt2 = input()\\nm, n = len(t1), len(t2)\\ndp = [[0]*(n+1) for _ in range(m+1)]\\nfor i in range(1, m+1):\\n    for j in range(1, n+1):\\n        if t1[i-1] == t2[j-1]: dp[i][j] = dp[i-1][j-1] + 1\\n        else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])\\nprint(dp[m][n])",
        "constraints": "1 <= text1.length, text2.length <= 1000",
        "examples": json.dumps([{"input": "text1='abcde', text2='ace'", "output": "3", "explanation": "LCS is 'ace'."}]),
        "starter_code": "text1 = input()\\ntext2 = input()\\n# Find longest common subsequence length\\n",
    },
]


def seed_data(db: Session):
    """Seed the database with demo data."""
    # Seed admin user
    admin = db.query(User).filter((User.email == "admin@preppilot.com") | (User.email == "admin@preppilot.local")).first()
    if not admin:
        admin = User(
            email="admin@preppilot.com",
            password_hash=hash_password("PrepPilot#2026"),
            full_name="PrepPilot Admin",
            is_admin=True,
            is_verified=True,
        )
        db.add(admin)
        logger.info("Created admin user: admin@preppilot.com")
    elif admin.email == "admin@preppilot.local":
        admin.email = "admin@preppilot.com"
        admin.password_hash = hash_password("PrepPilot#2026")
        db.add(admin)

    # Seed companies
    for c_data in COMPANIES:
        existing = db.query(Company).filter(Company.slug == c_data["slug"]).first()
        if not existing:
            company = Company(**c_data)
            db.add(company)
            logger.info(f"Seeded company: {c_data['name']}")

    # Seed coding questions
    for q_data in CODING_QUESTIONS:
        existing = db.query(CodingQuestion).filter(CodingQuestion.title == q_data["title"]).first()
        if not existing:
            question = CodingQuestion(**q_data)
            db.add(question)
            logger.info(f"Seeded question: {q_data['title']}")

    db.commit()
    logger.info("Database seeding complete!")
