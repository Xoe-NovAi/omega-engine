"""Error types for omega-sieve."""
# AP: AP-OMEGA-SIEVE-ERRORS-v1.0.0


class SieveError(Exception):
    """Base error for omega-sieve."""
    pass


class ScrapeError(SieveError):
    """Error during scraping."""
    pass


class VerificationError(SieveError):
    """Error during verification."""
    pass


class ProviderError(SieveError):
    """Error with an external provider."""
    pass


class BudgetExceededError(ProviderError):
    """API budget has been exceeded."""
    pass


class ProxyError(SieveError):
    """Error with proxy configuration."""
    pass


class ConfigError(SieveError):
    """Error in configuration."""
    pass


class YouTubeError(SieveError):
    """Error during YouTube extraction."""
    pass


class TranscriptionError(SieveError):
    """Error during transcription."""
    pass