import os
from Utils.Database.Database_Routing.add_database import add_database
from business.models import Business
from authentication.models import HigherStaffAccess
from staff.models import Staff


def is_user_in_business(user, business_id):
    db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"

    if not user:
        return False

    if user.role == 'owner':
        try:
            business = Business.objects.get(business_id=business_id)
            return business.owner_id == user.user_id
        except Business.DoesNotExist:
            return False

    elif user.role == 'higher-staff':
        try:
            access = HigherStaffAccess.objects.get(business_id=business_id, user_id=user.user_id)
            return access is not None
        except HigherStaffAccess.DoesNotExist:
            return False

    elif user.role == 'staff':
        try:
            add_database(db_name)
            staff = Staff.objects.using(db_name).get(user_id=user.user_id)
            return staff is not None
        except Staff.DoesNotExist:
            return False

    else:
        return False
