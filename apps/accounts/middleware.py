class ProxyIPMiddleware:
    """
    Forces Django to use the real IP address provided by Nginx,
    bypassing Gunicorn's Unix Socket paranoia.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        x_real_ip = request.META.get('HTTP_X_REAL_IP')

        if x_forwarded_for:
            request.META['REMOTE_ADDR'] = x_forwarded_for.split(',')[0].strip()
        elif x_real_ip:
            request.META['REMOTE_ADDR'] = x_real_ip

        return self.get_response(request)