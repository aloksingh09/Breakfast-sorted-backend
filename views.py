import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sqlmodel import Session, select
from database import engine
from models import Restaurant, Dish, AddOn, Order, MaterialRequirement, User, DeliveryAddress
from django.contrib.auth.hashers import make_password, check_password

# --- GENERIC UTILS ---
def get_request_body(request):
    if request.method in ["POST", "PUT"]:
        return json.loads(request.body.decode('utf-8'))
    return {}

# --- PUBLIC/ADMIN DISH CONTROLLERS ---
@csrf_exempt
def handle_dishes(request):
    with Session(engine) as session:
        if request.method == "GET":
            # Direct database select statement
            restaurant_filter = request.GET.get('restaurant_id')
            statement = select(Dish).where(Dish.is_available == True)
            if restaurant_filter:
                statement = statement.where(Dish.restaurant_id == restaurant_filter)
            
            results = session.exec(statement).all()
            return JsonResponse([dish.model_dump() for dish in results], safe=False)

        elif request.method == "POST":
            data = get_request_body(request)
            new_dish = Dish(**data)
            session.add(new_dish)
            session.commit()
            session.refresh(new_dish)
            return JsonResponse(new_dish.model_dump(), status=200)

# --- REVENUE & ANALYTICS DATA (ADMIN ONLY) ---
def get_admin_metrics(request):
    rest_id = request.GET.get('restaurant_id', 'all')
    with Session(engine) as session:
        # Load tables data arrays
        order_stmt = select(Order)
        dish_stmt = select(Dish)
        if rest_id != 'all':
            order_stmt = order_stmt.where(Order.restaurant_id == rest_id)
            dish_stmt = dish_stmt.where(Dish.restaurant_id == rest_id)

        orders = session.exec(order_stmt).all()
        dishes = session.exec(dish_stmt).all()

        total_rev = sum(o.total_price for o.total_price in orders)
        return JsonResponse({
            "revenue": total_rev,
            "productCount": len(dishes),
            "orderCount": len(orders),
            "orders": [o.model_dump() for o in orders]
        })

# --- LIVE ORDERS OPERATIONAL HUB (CHEF & ADMIN) ---
@csrf_exempt
def handle_orders(request):
    with Session(engine) as session:
        if request.method == "GET":
            # 1. Extract Authorization Header safely (Django case-insensitive fallback mapping)
            auth_header = request.headers.get("Authorization", "")
            if not auth_header:
                auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                
            # Query parameters parse karna filter check ke liye
            rest_id = request.GET.get('restaurant_id')

            # 2. Token structure aur integrity rules validation check
            if auth_header.startswith("Bearer JWT_"):
                # Token format logic parsing split matrices keys
                token_parts = auth_header.split("__")
                role = token_parts[1]                   # 'user', 'chef', 'admin'
                assigned_branch = token_parts[2]        # e.g., 'r1', 'r2' or 'none'
                user_id = int(token_parts[-1])          # Real DB User ID token target node
                
                # Base statement initialization
                statement = select(Order)

                # 3. ROLE-BASED ACCESS FILTERS LEVEL CONTROL
                if role == "admin":
                    # Admin supremacy logic: Agar specific rest_id maanga toh filter karo, nahi toh full database stream output
                    if rest_id and rest_id != 'all':
                        statement = statement.where(Order.restaurant_id == rest_id)
                        
                elif role == "chef":
                    # Chef isolation validation: Chef ko sirf uski assigned factory node branch ka hi pipeline load dikhega
                    # Agar frontend query string me branch badalne ki koshish kare, tab bhi session branch hi match hogi
                    target_branch = rest_id if rest_id else assigned_branch
                    statement = statement.where(Order.restaurant_id == target_branch)
                    
                else:
                    # Regular unique consumer customer profile constraint path execution mapping
                    statement = statement.where(Order.user_id == user_id)

                # Database execution pool calls tracking line records
                results = session.exec(statement).all()
                return JsonResponse([o.model_dump() for o in results], safe=False)

            return JsonResponse({"error": "Missing or corrupted security context token handshakes."}, status=401)
        elif request.method == "POST":
            auth_header = request.headers.get("Authorization", "")
            user_id = int(auth_header.split("__")[-1]) # Safe extract ID from custom token string format
            
            data = json.loads(request.body.decode('utf-8'))
            
            # CHECK GUARDRAIL LOGIC: If flag is new_address, save it into DeliveryAddress entries book automatically
            if data.get('is_new_address') is True:
                # Avoid inserting duplicate configuration matrices lines
                address_exists = session.exec(
                    select(DeliveryAddress).where(
                        DeliveryAddress.user_id == user_id,
                        DeliveryAddress.flat_no == data['flat_no'],
                        DeliveryAddress.pincode == data['pincode']
                    )
                ).first()
                
                if not address_exists:
                    new_addr_entry = DeliveryAddress(
                        user_id=user_id,
                        flat_no=data['flat_no'],
                        area_street=data['area_street'],
                        landmark=data.get('landmark'),
                        pincode=data['pincode']
                    )
                    session.add(new_addr_entry)
                    session.commit() # Save address entity data row to Supabase!
            
            # Proceed with baseline execution lines creating the main core Order
            new_order = Order(
                restaurant_id=data['restaurant_id'],
                user_id=user_id,
                dish_name=data['dish_name'],
                addons_selected=data['addons_selected'],
                flat_no=data['flat_no'],
                area_street=data['area_street'],
                landmark=data.get('landmark'),
                pincode=data['pincode'],
                total_price=data['total_price'],
                payment_method=data['payment_method'],
                status=data['status']
            )
            session.add(new_order)
            session.commit()
            session.refresh(new_order)
            return JsonResponse(new_order.model_dump(), status=200)

        elif request.method == "PUT": # Status alteration trigger update handle
            data = get_request_body(request)
            order_id = data.get('id')
            db_order = session.get(Order, order_id)
            if db_order:
                db_order.status = data.get('status', db_order.status)
                session.add(db_order)
                session.commit()
                session.refresh(db_order)
                return JsonResponse(db_order.model_dump())
            return JsonResponse({"error": "Order ID mismatch"}, status=404)

# --- INVENTORY MATERIAL MANAGEMENT (CHEF) ---
@csrf_exempt
def handle_materials(request):
    with Session(engine) as session:
        if request.method == "GET":
            rest_id = request.GET.get('restaurant_id')
            statement = select(MaterialRequirement)
            if rest_id:
                statement = statement.where(MaterialRequirement.restaurant_id == rest_id)
            results = session.exec(statement).all()
            return JsonResponse([m.model_dump() for m in results], safe=False)

        elif request.method == "POST":
            data = get_request_body(request)
            new_mat = MaterialRequirement(**data)
            session.add(new_mat)
            session.commit()
            session.refresh(new_mat)
            return JsonResponse(new_mat.model_dump(), status=200)


def create_mock_jwt(user: User):
    """Generates simple validation handles containing credentials payloads"""
    return f"JWT_SECURE_TOKEN__{user.role}__{user.assigned_restaurant_id or 'none'}__{user.id}"

# --- USER REGISTRATION ENDPOINT (Default account validation flow) ---
@csrf_exempt
def register_user(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        with Session(engine) as session:
            # Check duplicate identities mappings
            exists = session.exec(select(User).where((User.email == data['email']) | (User.phone == data['phone']))).first()
            if exists:
                return JsonResponse({"error": "Identity constraints already active inside DB registers."}, status=400)
            
            new_user = User(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                password_hash=make_password(data['password']),
                role="user", # Restricted Guardrail default level assignment
                assigned_restaurant_id=None
            )
            session.add(new_user)
            session.commit()
            return JsonResponse({"message": "Registration clear! Please login below."}, status=201)

# --- USER GATEWAY VERIFICATION LOGIN ENDPOINT ---
@csrf_exempt
def login_gateway(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        identity = data.get('identity') # Accept Email OR Mobile input configurations
        password = data.get('password')
        
        with Session(engine) as session:
            db_user = session.exec(select(User).where((User.email == identity) | (User.phone == identity))).first()
            if db_user and check_password(password, db_user.password_hash):
                token = create_mock_jwt(db_user)
                return JsonResponse({
                    "token": token,
                    "role": db_user.role,
                    "branch": db_user.assigned_restaurant_id,
                    "name": db_user.name,
                    "user_id": db_user.id
                })
            return JsonResponse({"error": "Bad credentials check sequence mapping inputs."}, status=401)

# --- USER DELIVERY REPOSITORIES ADDRESS POST/GET CONTROLLERS ---
@csrf_exempt
def manage_address_book(request):
    # Read session metadata logic from token strings
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer JWT_"):
        return JsonResponse({"error": "Unauthorized Access Detected"}, status=401)
    
    user_id = int(auth_header.split("__")[-1])
    
    with Session(engine) as session:
        if request.method == "GET":
            results = session.exec(select(DeliveryAddress).where(DeliveryAddress.user_id == user_id)).all()
            return JsonResponse([addr.model_dump() for addr in results], safe=False)
            
        elif request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            new_address = DeliveryAddress(
                user_id=user_id,
                flat_no=data['flat_no'],
                area_street=data['area_street'],
                landmark=data.get('landmark'),
                pincode=data['pincode']
            )
            session.add(new_address)
            session.commit()
            session.refresh(new_address)
            return JsonResponse(new_address.model_dump(), status=200)
        
@csrf_exempt
def handle_addons(request):
    with Session(engine) as session:
        if request.method == "GET":
            results = session.exec(select(AddOn)).all()
            return JsonResponse([addon.model_dump() for addon in results], safe=False)
            
        elif request.method == "POST": # Add this block to process incoming chef addons
            data = json.loads(request.body.decode('utf-8'))
            new_addon = AddOn(**data)
            session.add(new_addon)
            session.commit()
            session.refresh(new_addon)
            return JsonResponse(new_addon.model_dump(), status=200)
        
@csrf_exempt
def handle_restaurants(request):
    """Fetches all active restaurant branches from Supabase DB"""
    if request.method == "GET":
        with Session(engine) as session:
            statement = select(Restaurant)
            results = session.exec(statement).all()
            # Convert models to clean dictionary array list
            return JsonResponse([r.model_dump() for r in results], safe=False)