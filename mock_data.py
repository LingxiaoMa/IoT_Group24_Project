import random

def get_mock_data():
    return {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'values': [random.randint(20, 100) for _ in range(5)]
    }
