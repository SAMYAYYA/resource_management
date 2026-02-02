from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jose import jwt, JWTError
from .models import EmployeeInfo

from rest_framework.permissions import BasePermission 

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        print("auth_header : ",auth_header)
        if not auth_header:
            # raise AuthenticationFailed('Authorization header is required')
            return None


        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                raise AuthenticationFailed('Invalid token prefix')

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            print("payload of decoded jwt ",payload)
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Invalid token')

            user = EmployeeInfo.objects.get(id=user_id)

            print(f"user datas from JWT Token \n user id : {user_id} \n payload is : {payload}  \n user data is : {user}")

        except ValueError:
            raise AuthenticationFailed('Invalid Authorization header')
        except JWTError:
            raise AuthenticationFailed('Token expired or invalid')
        except EmployeeInfo.DoesNotExist:
            raise AuthenticationFailed('User not found')

        return (user, None)  # DRF sets request.user



class IsManager(BasePermission):
    message = "You must be a manager to access this."

    def has_permission(self, request, view):
        user = request.user

        print("user : ",user)
        if not user:
            return False

        # Check if user's role is Manager
        print (user.employee.role.role.lower() == "manager")

        return user.employee.role.role.lower() == "manager" 