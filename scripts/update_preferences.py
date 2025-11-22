"""
Script to add new interest preferences based on new courses.
"""
import csv
import random
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "synthetic"

def read_csv(filename):
    with open(DATA_DIR / filename, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def write_csv(filename, rows, fieldnames):
    with open(DATA_DIR / filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# Read data
preferences = read_csv('student_preferences.csv')
students = read_csv('students.csv')
enrollments = read_csv('enrollments.csv')

# New interests/skills from new courses
new_interests = [
    'deep-learning', 'neural-networks', 'ai-fundamentals', 'pattern-recognition',
    'statistical-learning', 'computational-geometry', 'algorithm-design',
    'virtual-reality', '3d-graphics', '3d-animation', 'data-visualization',
    'information-retrieval', 'search-algorithms', 'nosql', 'graph-databases',
    'functional-programming', 'privacy', 'cryptography'
]

# Map students who took new courses
student_new_course_map = {}
for enrollment in enrollments:
    course_id = enrollment['course_id']
    # Check if it's one of the new courses
    if course_id in ['MAC-COMP-8130', 'MAC-COMP-8207', 'MAC-COMP-8380', 'MAC-COMP-8390',
                     'MAC-COMP-8490', 'MAC-COMP-8500', 'MAC-COMP-8540', 'MAC-COMP-8570',
                     'MAC-COMP-8590', 'MAC-COMP-8610', 'MAC-COMP-8640', 'MAC-COMP-8700',
                     'MAC-COMP-8740', 'MAC-COMP-8790']:
        student_id = enrollment['student_id']
        if student_id not in student_new_course_map:
            student_new_course_map[student_id] = []
        student_new_course_map[student_id].append(course_id)

# Add new preferences for students
new_preferences = []
for student_id, courses in student_new_course_map.items():
    # Select 1-2 new interests for each student
    num_interests = random.randint(1, 2)
    selected_interests = random.sample(new_interests, num_interests)
    
    for interest in selected_interests:
        pref = {
            'student_id': student_id,
            'preference_type': 'skills_to_build',
            'preference_value': interest,
            'weight': round(random.uniform(0.5, 0.9), 2),
            'source': random.choice(['survey', 'advisor_note'])
        }
        new_preferences.append(pref)

# Also add some new career goals
career_goals = [
    'ai-engineer', 'ml-engineer', 'data-scientist', 'vr-developer',
    'algorithms-researcher', 'security-analyst', 'database-architect'
]

# Add career goals for 30% of students
sample_size = min(len(student_new_course_map), int(len(student_new_course_map) * 0.3))
if sample_size > 0:
    for student_id in random.sample(list(student_new_course_map.keys()), sample_size):
        goal = random.choice(career_goals)
        pref = {
            'student_id': student_id,
            'preference_type': 'career_goal',
            'preference_value': goal,
            'weight': round(random.uniform(0.7, 0.95), 2),
            'source': 'survey'
        }
        new_preferences.append(pref)

# Combine old and new
all_preferences = preferences + new_preferences

# Write updated preferences
fieldnames = preferences[0].keys()
write_csv('student_preferences.csv', all_preferences, fieldnames)

print(f"[OK] Added {len(new_preferences)} new preferences")
print(f"[OK] Total preferences: {len(all_preferences)}")
print(f"[OK] Students updated: {len(student_new_course_map)}")
print(f"[OK] File updated: {DATA_DIR / 'student_preferences.csv'}")

