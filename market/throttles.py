from rest_framework.throttling import SimpleRateThrottle


class RoleBasedDailyQuoteThrottle(SimpleRateThrottle):

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        role = getattr(request.user, "role", "basic")
        return f"throttle_quote_{role}_{request.user.pk}"

    def get_rate(self):
        return None

    def allow_request(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True

        role = getattr(request.user, "role", "basic")
        if role == "pro":
            self.rate = "100/day"
        else:
            self.rate = "10/day"

        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)
