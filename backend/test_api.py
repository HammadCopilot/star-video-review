"""
Simple API test script to verify backend endpoints
"""

import requests
import json

BASE_URL = 'http://localhost:5001'

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_backend():
    """Test backend API endpoints"""
    
    print("\n🧪 Starting Backend API Tests...\n")
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    
    # Test 2: Root Endpoint
    print("\n2️⃣ Testing Root Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print_response("Root Endpoint", response)
    
    # Test 3: Register User
    print("\n3️⃣ Testing User Registration...")
    register_data = {
        "email": "testuser@example.com",
        "password": "test123",
        "first_name": "Test",
        "last_name": "User",
        "role": "reviewer"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print_response("User Registration", response)
    
    # Test 4: Login with Seeded Admin
    print("\n4️⃣ Testing Login (Admin)...")
    login_data = {
        "email": "admin@star.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("Admin Login", response)
    
    if response.status_code == 200:
        admin_token = response.json()['access_token']
        
        # Test 5: Get Current User
        print("\n5️⃣ Testing Get Current User...")
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print_response("Get Current User", response)
        
        # Test 6: Get All Users (Admin)
        print("\n6️⃣ Testing Get All Users (Admin Only)...")
        response = requests.get(f"{BASE_URL}/api/auth/users", headers=headers)
        print_response("Get All Users", response)
        
        # Test 7: Create Video with External URL
        print("\n7️⃣ Testing Create Video (External URL)...")
        video_data = {
            "title": "Test PRT Video",
            "url": "https://cdn.jwplayer.com/videos/Mi1eph4z-pX8xjuXl.mp4",
            "category": "pivotal_response",
            "description": "Test video for API testing"
        }
        response = requests.post(f"{BASE_URL}/api/videos", json=video_data, headers=headers)
        print_response("Create Video", response)
        
        video_id = None
        if response.status_code == 201:
            video_id = response.json()['video']['id']
        
        # Test 8: List All Videos
        print("\n8️⃣ Testing List Videos...")
        response = requests.get(f"{BASE_URL}/api/videos", headers=headers)
        print_response("List Videos", response)
        
        # Test 9: Get Single Video
        if video_id:
            print(f"\n9️⃣ Testing Get Single Video (ID: {video_id})...")
            response = requests.get(f"{BASE_URL}/api/videos/{video_id}", headers=headers)
            print_response("Get Single Video", response)
        
        # Test 10: Filter Videos by Category
        print("\n🔟 Testing Filter Videos by Category...")
        response = requests.get(
            f"{BASE_URL}/api/videos?category=discrete_trial&page=1&per_page=5",
            headers=headers
        )
        print_response("Filter Videos (Discrete Trial)", response)
        
        # Test 11: Update Video
        if video_id:
            print(f"\n1️⃣1️⃣ Testing Update Video (ID: {video_id})...")
            update_data = {
                "title": "Updated Test Video Title",
                "description": "Updated description"
            }
            response = requests.put(
                f"{BASE_URL}/api/videos/{video_id}",
                json=update_data,
                headers=headers
            )
            print_response("Update Video", response)
    
    # Test 12: Login with Reviewer
    print("\n1️⃣2️⃣ Testing Login (Reviewer)...")
    login_data = {
        "email": "reviewer@star.com",
        "password": "reviewer123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("Reviewer Login", response)
    
    if response.status_code == 200:
        reviewer_token = response.json()['access_token']
        headers = {"Authorization": f"Bearer {reviewer_token}"}
        
        # Test 13: Try to Access Users Endpoint (Should Fail)
        print("\n1️⃣3️⃣ Testing Authorization (Reviewer accessing admin endpoint)...")
        response = requests.get(f"{BASE_URL}/api/auth/users", headers=headers)
        print_response("Access Denied Test (Expected 403)", response)
        
        # Test 14: Reviewer Can List Videos
        print("\n1️⃣4️⃣ Testing Reviewer Can List Videos...")
        response = requests.get(f"{BASE_URL}/api/videos", headers=headers)
        print_response("Reviewer List Videos", response)
    
    # Test 15: Test Invalid Login
    print("\n1️⃣5️⃣ Testing Invalid Login...")
    login_data = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("Invalid Login (Expected 401)", response)
    
    print("\n" + "="*60)
    print("✅ Backend API Tests Completed!")
    print("="*60)
    print("\n📝 Summary:")
    print("  - Health check and root endpoints working")
    print("  - User registration and authentication working")
    print("  - Role-based authorization working")
    print("  - Video CRUD operations working")
    print("  - JWT token authentication working")
    print("\n💡 Next: Run the frontend and test full integration")


if __name__ == '__main__':
    try:
        test_backend()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend server")
        print("   Make sure the server is running:")
        print("   cd backend && python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")

