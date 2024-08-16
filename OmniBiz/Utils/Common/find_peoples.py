from django.contrib.auth import get_user_model

User = get_user_model()


def get_all_users():
    return User.objects.exclude(role='admin')


def get_user_by_id(user_id):
    return User.objects.filter(user_id=user_id).first()


def get_business_people(business_id):
    from business.models import Business
    from authentication.models import HigherStaffAccess

    # Fetch the business owner
    business = Business.objects.filter(business_id=business_id).first()
    owner = User.objects.filter(user_id=business.owner_id).first() if business else None

    # Fetch higher-staff
    higher_staff = User.objects.filter(
        user_id__in=HigherStaffAccess.objects.filter(business_id=business_id).values_list('user_id', flat=True))

    # Fetch staff
    staff = User.objects.filter(business_id=business_id)

    # Exclude admins
    people = User.objects.filter(user_id__in=[owner.user_id] + list(higher_staff.values_list('user_id', flat=True)) + list(
        staff.values_list('user_id', flat=True))).exclude(role='admin')

    return people
