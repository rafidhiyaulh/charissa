from charissa.api.rate_limit import RateLimiter


def _limiter_with_fake_clock(max_requests: int, window_seconds: float):
    fake_time = [0.0]
    limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds, clock=lambda: fake_time[0])
    return limiter, fake_time


def test_allows_up_to_max_requests_in_window():
    limiter, _ = _limiter_with_fake_clock(max_requests=3, window_seconds=60)

    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True


def test_blocks_requests_over_the_limit():
    limiter, _ = _limiter_with_fake_clock(max_requests=2, window_seconds=60)

    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is False


def test_resets_after_window_passes():
    limiter, fake_time = _limiter_with_fake_clock(max_requests=1, window_seconds=60)

    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is False

    fake_time[0] = 61.0
    assert limiter.allow("client-a") is True


def test_keys_are_independent():
    limiter, _ = _limiter_with_fake_clock(max_requests=1, window_seconds=60)

    assert limiter.allow("client-a") is True
    assert limiter.allow("client-b") is True
    assert limiter.allow("client-a") is False
