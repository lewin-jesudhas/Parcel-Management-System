from abc import ABC, abstractmethod
import re

# Strategy interfaces
class EmployeeIDValidationStrategy(ABC):
    @abstractmethod
    def validate(self, employee_id):
        pass

class PasswordValidationStrategy(ABC):
    @abstractmethod
    def validate(self, password):
        pass

# Concrete implementations of strategies
class RegexEmployeeIDValidation(EmployeeIDValidationStrategy):
    def validate(self, employee_id):
        # Validate employee ID using regex
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', employee_id))

class RegexPasswordValidation(PasswordValidationStrategy):
    def validate(self, password):
        # Validate password using regex
        return bool(re.match(r'^[a-zA-Z0-9!@#$%^&*()_-]+$', password))

# Context class that uses the strategies
class ValidationContext:
    def __init__(self, strategy, data):
        self.strategy = strategy
        self.data = data

    def validate(self):
        return self.strategy.validate(self.data)
