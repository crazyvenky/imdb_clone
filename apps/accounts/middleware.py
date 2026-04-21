from django.shortcuts import redirect
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


class EnforceDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        
        # If someone visits the raw IP, instantly redirect them to the .nip.io domain!
        if host == '16.112.125.230':
            # request.get_full_path() ensures if they go to /movies/1, it redirects to .nip.io/movies/1
            return redirect(f"http://16.112.125.230.nip.io{request.get_full_path()}")
            
        return self.get_response(request)