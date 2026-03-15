import os
import time
from app.modules.users import repository as user_repo
from app.modules.communities import repository as comm_repo
from app.modules.offers import repository as offer_repo
from app.modules.transactions import repository as trans_repo
from app.modules.reviews import repository as review_repo
from app.modules.notifications import repository as notif_repo
from app.db import get_db_cursor

# Setup env for test (assuming local default if not set)
# os.environ['DB_PASSWORD'] = 'your_password' # User needs to set this if generic fails

def run_verification():
    print("Starting Verification Flow...")
    
    # 1. Create Users
    print("\n1. Creating Users...")
    try:
        buyer = user_repo.create_user(
            username=f"buyer_{int(time.time())}", 
            email=f"buyer_{int(time.time())}@test.com", 
            password_hash="hash", 
            latitude=40.7128, 
            longitude=-74.0060 # NYC
        )
        seller = user_repo.create_user(
            username=f"seller_{int(time.time())}", 
            email=f"seller_{int(time.time())}@test.com", 
            password_hash="hash", 
            latitude=40.7306, 
            longitude=-73.9352 # Brooklyn (Near NYC)
        )
        print(f"   Created Buyer: {buyer['username']} (ID: {buyer['id']})")
        print(f"   Created Seller: {seller['username']} (ID: {seller['id']})")
    except Exception as e:
        print(f"   Failed to assign/create users (maybe schema not applied?): {e}")
        return

    # 2. Check Proximity
    print("\n2. Checking Proximity (User Search)...")
    try:
        nearby_users = user_repo.get_users_nearby(40.7128, -74.0060, radius_km=10)
        found = any(u['id'] == seller['id'] for u in nearby_users)
        print(f"   Seller found nearby? {found}")
    except Exception as e:
         print(f"   Failed: {e}")

    # 3. Create Community & Join
    print("\n3. Community Management...")
    try:
        comm_name = f"Readers_{int(time.time())}"
        print(f"   Attempting to create community: {comm_name}")
        comm = comm_repo.create_community(comm_name)
        if comm:
            print(f"   Created Community: {comm['name']} (ID: {comm['id']})")
            comm_repo.add_member(seller['id'], comm['id'], role='admin')
            comm_repo.add_member(buyer['id'], comm['id'], role='member')
            members = comm_repo.get_community_members(comm['id'])
            print(f"   Community Members Count: {len(members)}")
        else:
            print("   Created community but got None return value.")
    except Exception as e:
        print(f"   Failed to create community: {e}")
        if hasattr(e, 'pgerror'):
            print(f"   PG Error: {e.pgerror}")

    # 4. Create Offer
    print("\n4. Creating Book Offer...")
    try:
        # Need a book first, assume book_id 1 exists or mock it? 
        # For raw SQL, foreign key constraints might fail if book table empty.
        # Let's try to insert a dummy book directly first.
        with get_db_cursor(commit=True) as cur:
            cur.execute("INSERT INTO book (title, isbn) VALUES ('Test Book', '12345') RETURNING id")
            book_id = cur.fetchone()['id']
            
        offer = offer_repo.create_book_offer(
            offer_type='SELL', price=15.00, condition='Good', quantity=1, 
            user_id=seller['id'], book_id=book_id,
            latitude=40.7306, longitude=-73.9352
        )
        print(f"   Created Offer ID: {offer['id']}")
    except Exception as e:
         print(f"   Failed: {e}")
         return

    # 5. Search Offers
    print("\n5. Searching Offers (Geographical)...")
    try:
        results = offer_repo.search_offers(
            latitude=40.7128, longitude=-74.0060, radius_km=10
        )
        found_offer = any(o['id'] == offer['id'] for o in results)
        print(f"   Offer found in radius? {found_offer}")
        if results:
             print(f"   Distance to offer: {results[0].get('distance')} km")
    except Exception as e:
         print(f"   Failed: {e}")

    # 6. Transaction & Notification
    print("\n6. Transaction & Notification Triggers...")
    try:
        tx = trans_repo.create_transaction(
            status='pending', final_price=15.00, 
            buyer_id=buyer['id'], seller_id=seller['id'], book_offer_id=offer['id']
        )
        print(f"   Transaction Created: ID {tx['id']}")
        
        # Update status to completed -> should trigger notification & allow trust score update
        trans_repo.update_transaction(tx['id'], status='completed')
        print("   Transaction updated to 'completed'")
        
        # Check Notification
        notifs = notif_repo.get_notifications(seller['id'])
        # Expecting 'status_change' notification
        has_notif = any('completed' in n['message'] for n in notifs)
        print(f"   Seller received notification? {has_notif}")
    except Exception as e:
         print(f"   Failed: {e}")

    # 7. Review & Trust Score
    print("\n7. Review & Trust Score...")
    try:
        # Buyer reviews Seller
        review_repo.create_review(
            user_id=seller['id'], # Target is seller
            book_id=book_id,
            transaction_id=tx['id'],
            rating=5,
            comment="Great seller!"
        )
        print("   Review created.")
        
        # Check Trust Score
        updated_seller = user_repo.get_user_by_id(seller['id'])
        print(f"   Seller New Trust Score: {updated_seller.get('trust_score')}")
    except Exception as e:
         print(f"   Failed: {e}")

if __name__ == "__main__":
    run_verification()
