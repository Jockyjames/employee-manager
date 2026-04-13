from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware léger — le logging détaillé est fait dans les vues.
    Ici on peut tracer des accès automatiques si besoin.
    """
    EXCLUDED_PATHS = ['/static/', '/media/', '/favicon.ico', '/admin/jsi18n/']

    def process_request(self, request):
        for path in self.EXCLUDED_PATHS:
            if request.path.startswith(path):
                return None
        return None
