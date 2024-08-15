import os

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from Utils.Database.Database_Routing.add_database import add_database
from business.models import Business
from authentication.models import HigherStaffAccess
from staff.models import Staff


@database_sync_to_async
def get_business_owner(business_id):
    try:
        business = Business.objects.get(business_id=business_id)
        return business.owner_id
    except Business.DoesNotExist:
        return None


@database_sync_to_async
def get_higher_staff_access(business_id, user_id):
    try:
        return HigherStaffAccess.objects.get(business_id=business_id, user_id=user_id)
    except HigherStaffAccess.DoesNotExist:
        return None


@database_sync_to_async
def get_staff(business_id, user_id):
    db_name = f"{business_id}{os.getenv('DB_NAME_SECONDARY')}"
    add_database(db_name)
    try:
        return Staff.objects.using(db_name).get(user_id=user_id)
    except Staff.DoesNotExist:
        return None


async def is_user_in_business(user, business_id):
    if not user or not user.is_authenticated:
        return False

    if user.role == 'owner':
        owner_id = await get_business_owner(business_id)
        return owner_id == user.user_id

    elif user.role == 'higher-staff':
        access = await get_higher_staff_access(business_id, user.user_id)
        return access is not None

    elif user.role == 'staff':
        staff = await get_staff(business_id, user.user_id)
        return staff is not None

    return False
