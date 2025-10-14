class ContentTypeError(Exception):
    def __init__(self, message: str, status: int, headers: dict):
        super().__init__(message)
        self.status = status
        self.headers = headers
        
class TooManyRedirects(Exception):
    pass
    
class NotImplementedWarning(Warning):
    pass