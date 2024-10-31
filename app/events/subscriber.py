from typing import Dict
from pyee.asyncio import AsyncIOEventEmitter
from app.events.fuel_log import FuelLogged
from app.events.user import InviteAccepted









class Subscriber:
    """
        The Subscriber class is responsible for registering handlers for events.
    """

    _instance = None

    event_to_handler_mapping: Dict = {
        FuelLogged: [],
        InviteAccepted: [], 
    }


    def __new__(cls):
        """
        Override __new__ method to implement Singleton pattern.
        """
        if not cls._instance:
            cls._instance = super(Subscriber, cls).__new__(cls)
            cls._instance.events = AsyncIOEventEmitter()
            cls._instance._subscribe_to_events()
        return cls._instance
    

    def _subscribe_to_events(self):
        """
        Method to subscribe handlers to events during instantiation.
        """
        for event, handlers in self.event_to_handler_mappings.items():
            for handler in handlers:
                self.events.on(event, handler)


    def subscribe(self, event, handler):
        self.events.on(event, handler)


    def publish(self, event, data):
        self.events.emit(event, data)




# Initialize the Subscriber instance
subscriber = Subscriber()


