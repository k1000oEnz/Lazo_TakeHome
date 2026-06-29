class DomainError(Exception):
    pass


class InvalidTransitionError(DomainError):
    pass


class MissingDocumentError(DomainError):
    pass


class ConcurrencyConflictError(DomainError):
    pass
