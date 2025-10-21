from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import jsonify

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt() or {}
            user_role = claims.get("role")
            if roles and user_role not in roles:
                return jsonify({"error": "forbidden", "detail": "insufficient role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
