import random
import string

def generate_tracking_number(length=10, existing_ids=set()):
    characters = string.ascii_uppercase + string.digits
    
    while True:
        tracking_number = ''.join(random.choice(characters) for _ in range(length))
        tracking_id = "ST" + tracking_number
        
        if tracking_id not in existing_ids:
            existing_ids.add(tracking_id)
            return tracking_id
        
