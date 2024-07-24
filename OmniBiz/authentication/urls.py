from django.urls import path

from authentication.views import (CreateUserView,
                                  LoginView,
                                  ActivateAccountView,
                                  PasswordResetRequestView,
                                  PasswordResetConfirmView,
                                  PasswordChangeView,
                                  CreateAdminView,
                                  CreateStaffView,
                                  OwnerAction,
                                  AdminAction,
                                  StaffAction,
                                  CreateHigherStaffView, LogoutView,
                                  )

urlpatterns = [
    path('create-owner', CreateUserView.as_view(), name='create owner'),
    path('create-staff', CreateStaffView.as_view(), name='create staff'),
    path('create-admin', CreateAdminView.as_view(), name='create admin'),
    path('update-higher-staff/<str:user_id>', CreateHigherStaffView.as_view(), name='create admin'),
    path('login', LoginView.as_view(), name='login'),
    path('verify/<str:user_id>/<str:token>', ActivateAccountView.as_view(), name='verify'),
    path('reset-account-request', PasswordResetRequestView.as_view(), name='request-reset'),
    path('password-reset/<uid>/<token>', PasswordResetConfirmView.as_view(), name='password-reset'),
    path('change-password', PasswordChangeView.as_view(), name='change-password'),
    path('owner-action/<str:user_id>', OwnerAction.as_view(), name='owner-action'),
    path('admin-action', AdminAction.as_view(), name='owner-action'),
    path('staff-action', StaffAction.as_view(), name='owner-action'),
    path('logout', LogoutView.as_view(), name='logout'),

]
