from django.urls import re_path
from myapp.consumers import OrderTrackingConsumer, AdminDriverTrackingConsumer


websocket_urlpatterns = [

    #.....user tracking order.....
    re_path(r"ws/track/(?P<order_id>[0-9a-fA-F]+)/$", OrderTrackingConsumer.as_asgi()),




#.....admin tracking drivers.....

    re_path(r"ws/admin/drivers/$", AdminDriverTrackingConsumer.as_asgi()),
]
