from functools import wraps
from flask_login import current_user

def department_required(required_department):
    """
    Decorator to check if a user belongs to a specific department.

    Args:
        required_department (str): The name of the department required for access.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            The wrapper function that performs the department check.
            Assumes the 'user' object passed to the decorated function
            has a 'department' attribute.
            """
            user = current_user

            if user is None:
                raise AttributeError("User not found.")
            elif user.department == required_department:
                return func(*args, **kwargs)
            else:
                raise PermissionError(f"User is not authorized. Requires '{required_department}' department.")
        return wrapper
    return decorator

def permission_required(*required_permissions):
    """
    Decorator to check if a user roles have specific permissions.

    Args:
        required_permissions (*str): The name of the permissions required for access.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            The wrapper function that performs the permission check.

            """
            user = current_user
            if user is None:
                raise AttributeError("User not found.")

            permissions = []
            for role in user.roles:
                if role.permissions:
                    for permission in role.permissions:
                        if permission.name not in permissions:
                            permissions.append(permission.name)
                            print(permission.name)

            for r_permission in required_permissions:
                print(r_permission)
                if r_permission in permissions:
                    return func(*args, **kwargs)
        
            return ("<h1>Forbidden</h1> You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.")
        return wrapper
    return decorator
