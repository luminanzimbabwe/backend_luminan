from django.urls import re_path
from myapp.consumers import (
    OrderTrackingConsumer,
    AdminDriverTrackingConsumer,
    DriverTrackingConsumer,  # 👈 add this
)

websocket_urlpatterns = [
    # User tracking their own order
    re_path(r"ws/track/(?P<order_id>[0-9a-fA-F]+)/$", OrderTrackingConsumer.as_asgi()),

    # Admin tracking all drivers
    re_path(r"ws/admin/drivers/$", AdminDriverTrackingConsumer.as_asgi()),

    # Driver’s own live location channel 👇
    re_path(r"ws/driver/track/(?P<driver_id>[0-9a-fA-F]+)/$", DriverTrackingConsumer.as_asgi()),
]
