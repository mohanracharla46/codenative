
import sys
import os
sys.path.append(os.getcwd())

from app import app
import json

with app.test_client() as client:
    # Get any python topic slug from the list first
    res_list = client.get('/api/content/python')
    topics = res_list.get_json()
    if topics and len(topics) > 0:
        slug = topics[0]['topic_slug']
        response = client.get(f'/api/content/python/{slug}')
        print(json.dumps(response.get_json(), indent=2))
    else:
        print("No topics found for python")
