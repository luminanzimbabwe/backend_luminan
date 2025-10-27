# myapp/email_utils.py

import ssl
from django.core.mail.backends.smtp import EmailBackend
import traceback

class CustomEmailBackend(EmailBackend):
    """
    Custom email backend that bypasses SSL certificate verification.
    ONLY USE IN DEVELOPMENT/TESTING.
    """
    def open(self):
        if self.connection:
            return True
        try:
            # Create an unverified SSL context for development only
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE 

            # Call the parent open method which uses this context
            return super().open()
        
        except Exception as e:
            # 🛑 CRITICAL DEBUGGING: Print the exact error here to ensure we see it.
            print(f"!!! DEBUG - CustomEmailBackend ERROR: {e.__class__.__name__}: {e}")
            if not self.fail_silently:
                # Re-raise the exception so it propagates to your dispatch function's catch block
                raise