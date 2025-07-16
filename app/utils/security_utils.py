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

            print(user.department, required_department)

            if user is None:
                raise AttributeError("User not found.")
            elif user.department == required_department:
                return func(*args, **kwargs)
            else:
                raise PermissionError(f"User is not authorized. Requires '{required_department}' department.")
        return wrapper
    return decorator
