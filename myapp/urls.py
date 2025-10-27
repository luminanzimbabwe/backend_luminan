from django.urls import path
from django.http import HttpResponse

# === Import all views (assuming they are all correctly imported as they were) ===
from .views import (
    # User Authentication
    register_user, verify_otp, login_user, forgot_password, reset_password, logout_user, delete_account,
    # User Profile (Assuming get_current_user is the correct name)
    get_current_user,
    # Orders
    start_gas_order, finalize_gas_order, list_user_orders, get_order_detail, cancel_order,
    # Notifications
    get_user_notifications, mark_notification_read, mark_all_notifications_read,
    # Drivers
    register_driver, get_order_tracking_details, login_driver, driver_assigned_orders, driver_get_order, mark_delivered, driver_performance_metrics, confirm_order,
    set_price_per_kg, update_driver_location, verify_driver_otp,
    # Admin Auth
  
     logout_admin, 
    # Utilities
    send_test_sms, track_order, refresh_token, get_order_status, paynow_update_view, chat_with_gpt,
)





# === Import admin management views (imported under the 'views' alias) ===
from . import views


# === Homepage ===
def homepage(request):
    return HttpResponse("Welcome to the LuminaN Gas App API v1!")


# === URL Patterns ===
urlpatterns = [
    # -----------------
    # Homepage / Root
    # -----------------
    path('', homepage, name='homepage'),
    path('test/sms/', send_test_sms, name='send_test_sms'),


    # #######################################################################
    # 1. USER AUTH & PROFILE (/api/v1/user/...)
    # #######################################################################

    # --- User Authentication & Security ---
    path('api/v1/user/register/', register_user, name='user_register'),
    path('api/v1/user/verify/', verify_otp, name='user_verify_otp'),
    path('api/v1/user/login/', login_user, name='user_login'),
    path('api/v1/user/logout/', logout_user, name='user_logout'),
    path('api/v1/user/forgot-password/', forgot_password, name='user_forgot_password'),
    path('api/v1/user/reset-password/', reset_password, name='user_reset_password'),
    path('api/v1/user/delete-account/', delete_account, name='user_delete_account'),

    # --- Profile & Settings ---
    path('api/v1/user/profile/', get_current_user, name='user_profile'),


    path('api/v1/user/refresh/', refresh_token, name='token_refresh'),

  


    # #######################################################################
    # 2. ORDERS (/api/v1/orders/...)
    # #######################################################################

    path('api/v1/orders/start/', start_gas_order, name='order_start_quote'),
    path('api/v1/orders/finalize/', finalize_gas_order, name='order_finalize'),
    path('api/v1/orders/my-orders/', list_user_orders, name='order_list_user'),
    path('api/v1/orders/<str:order_id>/', get_order_detail, name='order_detail'),
    path('api/v1/orders/<str:order_id>/cancel/', cancel_order, name='order_cancel'),
    path('api/v1/orders/<str:order_id>/track/', track_order, name='order_track'), # From tracking view\
    
    
    
    
    # NEW (Correct prefix)
    path('api/v1/orders/<str:order_id>/status/', get_order_status, name='order-status'),

    # #######################################################################
    # 3. NOTIFICATIONS (/api/v1/notifications/...)
    # #######################################################################

    path('api/v1/notifications/', get_user_notifications, name='notifications_list'),
    path('api/v1/notifications/mark-all-read/', mark_all_notifications_read, name='notifications_mark_all_read'),
    path('api/v1/notifications/<str:notification_id>/read/', mark_notification_read, name='notifications_mark_read'),


    # #######################################################################
    # 4. DRIVERS (/api/v1/driver/...)
    # #######################################################################

    # --- Driver Auth & Management ---
    path('api/v1/driver/register/', register_driver, name='driver_register'),
    path('api/v1/driver/login/', login_driver, name='driver_login'),
    path('api/v1/driver/profile/<str:driver_id>/', views.get_driver_profile, name='driver_profile'),
    path('api/v1/driver/orders/', driver_assigned_orders, name='driver_list_assigned_orders'),
    path('api/v1/driver/location/update/', update_driver_location, name='driver_update_location'),
    path('api/v1/driver/pricing/set/', set_price_per_kg, name='driver_set_price'),
    

    # Driver OTP verification
    path('api/v1/driver/verify-otp/', verify_driver_otp, name='driver_verify_otp'),




    path('paynow/update', paynow_update_view, name='paynow_update'),


        # --- Driver Order Actions ---
    path('api/v1/driver/orders/<str:order_id>/confirm/', confirm_order, name='driver_order_confirm'),
    path('api/v1/driver/orders/<str:order_id>/cancel/', cancel_order, name='driver_order_cancel'), # Reusing user cancel logic
    path('api/v1/driver/orders/<str:order_id>/delivered/', mark_delivered, name='driver_order_mark_delivered'),
   
   
   
   
    path('api/v1/driver/<str:driver_id>/performance/', driver_performance_metrics, name='driver-performance'),
    path('api/v1/orders/<str:order_id>/tracking-details/', get_order_tracking_details, name='order-tracking-details'),
    path('api/v1/driver/driver/orders/<str:order_id>/', driver_get_order, name='driver-get-order'),






    # --- Driver Earnings & Financial ---
    
    
    path('api/v1/driver/wallet/', views.get_driver_wallet, name='driver_wallet'),
   
    # --- Driver Availability & Schedule ---
   
   
    path('api/v1/driver/break/start/', views.start_break, name='driver_start_break'),
    path('api/v1/driver/break/end/', views.end_break, name='driver_end_break'),
    
    # --- Driver Statistics & Performance ---
   
    path('api/v1/driver/performance/', views.get_driver_performance, name='driver_performance'),
    
   
    
    path('api/v1/driver/delivery-history/', views.get_delivery_history, name='driver_delivery_history'),
   
  
   

    # #######################################################################
    # 5. SUPER ADMIN AUTH (/api/v1/admin/auth/...)
    # #######################################################################

  
   
   
    path('api/v1/admin/auth/logout/', logout_admin, name='admin_logout'),
   
    
    # --- Admin Recovery ---
    
  
   


    # #######################################################################
    # 6. SUPER ADMIN MANAGEMENT (/api/v1/admin/...)
    # #######################################################################

    # --- General/Dashboard ---
    path('api/v1/admin/dashboard/', views.get_admin_dashboard_overview, name='admin_dashboard_overview'),
    path('api/v1/admin/overview/', views.system_overview, name='admin_system_overview'),
    path('api/v1/admin/logs/', views.view_activity_logs, name='admin_view_activity_logs'),
    

    path('api/v1/admin/system/health/', views.system_health_check, name='admin_system_health_check'),

    # --- User Management ---
    path('api/v1/admin/users/', views.get_all_users, name='admin_get_all_users'),
   
   
   

    # --- Driver Management ---
    path('api/v1/admin/drivers/', views.get_all_drivers, name='admin_get_all_drivers'),
    path('api/v1/admin/drivers/track-all/', views.track_all_drivers, name='admin_track_all_drivers'),
   
   
    path('api/v1/admin/drivers/<str:driver_id>/', views.get_driver_details, name='admin_get_driver_details'),
    path('api/v1/admin/drivers/<str:driver_id>/track/', views.track_driver_location, name='admin_track_driver_location'),
   
    
   
    
    # --- Order Management ---
    path('api/v1/admin/orders/', views.get_all_orders, name='admin_get_all_orders'),
    path('api/v1/admin/orders/overview/', views.order_overview_stats, name='admin_order_overview_stats'),
    
   
    path('api/v1/admin/orders/<str:order_id>/modify/', views.modify_order, name='admin_modify_order'),
   
    # --- Financials & Reports ---
    path('api/v1/admin/transactions/', views.view_all_transactions, name='admin_view_all_transactions'),
   
   
    path('api/v1/admin/reports/sales/', views.sales_performance_report, name='admin_sales_report'),
    path('api/v1/admin/reports/drivers/', views.driver_performance_report, name='admin_driver_report'),

   
   
    path('api/v1/admin/pricing/update/', views.update_pricing, name='admin_update_pricing'),
  

    # --- Inventory Management ---
   
   
    
   
    
    
   












    # 1. GET: List all orders for the admin dashboard table (READ)
path('api/admin/orders/', views.admin_get_all_orders, name='admin-all-orders'),

# 2. POST: Update status/driver for a specific order (UPDATE)
path('api/admin/orders/<str:order_id>/update/', views.admin_update_order_details, name='admin-update-order'),
path('api/admin/users/', views.admin_get_all_users, name='admin-all-users'),
path('api/admin/users/details/', views.admin_get_all_user_details, name='admin-all-users-details'),
# DELETE: Remove a specific user
path('api/admin/users/<str:user_id>/delete/', views.admin_delete_user, name='admin-delete-user'),


# GET: Total number of drivers
path('api/admin/drivers/count/', views.admin_get_driver_count, name='admin-driver-count'),
path(
        'api/admin/orders/revenue/', 
        views.admin_get_total_revenue, 
        name='admin-orders-revenue'
    ),

path(
    'api/admin/sales/volume/', 
    views.admin_sales_volume, 
    name='admin-sales-volume'
),

# urls.py



# urls.py
path('api/admin/orders/details/', views.admin_get_all_orders_details, name='admin-all-orders-details'),


# Driver Details
path("api/admin/drivers/<str:driver_id>/", views.admin_get_driver_details, name="admin-driver-details"),


# All Drivers (Admin)
path("api/admin/drivers/", views.admin_get_all_drivers, name="admin-all-drivers"),


 path('admin/orders/<str:order_id>/update-unit-price/', views.admin_update_order_unit_price, name='admin-update-unit-price'),



path('admin/global-price/update/', views.admin_update_global_price, name='admin-update-global-price'),



#########  gpt $$########
path('api/v1chat-gpt/', chat_with_gpt, name='chat_gpt'),

]
