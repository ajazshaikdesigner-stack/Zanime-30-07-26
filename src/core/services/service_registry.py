"""
Service Registry for dependency injection and singleton management.
"""
import threading
from typing import TypeVar, Type, Callable, Dict, Any

T = TypeVar('T')

class ServiceRegistry:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ServiceRegistry, cls).__new__(cls)
                cls._instance._services: Dict[Type, Any] = {}
                cls._instance._factories: Dict[Type, Callable[[], Any]] = {}
                cls._instance._service_lock = threading.Lock()
        return cls._instance

    def register(self, service_class: Type[T], instance: T):
        """Register an active singleton instance."""
        with self._service_lock:
            self._services[service_class] = instance
            
    def register_factory(self, service_class: Type[T], factory: Callable[[], T]):
        """Register a lazy-loader for a service."""
        with self._service_lock:
            self._factories[service_class] = factory

    def get(self, service_class: Type[T]) -> T:
        """Retrieve the initialized singleton, invoking the factory if not yet instantiated."""
        with self._service_lock:
            if service_class in self._services:
                return self._services[service_class]
            
            if service_class in self._factories:
                instance = self._factories[service_class]()
                self._services[service_class] = instance
                return instance
                
        raise KeyError(f"Service {service_class.__name__} not found in registry.")
        
    def clear(self):
        """Wipe the registry for lifecycle teardown."""
        with self._service_lock:
            self._services.clear()
            self._factories.clear()

# Global singleton instance for easy imports
registry = ServiceRegistry()
