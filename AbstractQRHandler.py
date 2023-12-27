from abc import ABC
from abc import abstractmethod

class AbstractQRHandler(ABC):
    @abstractmethod    
    def scan_qr(self):
        pass

    @abstractmethod
    def generate_otp(self):
        pass
