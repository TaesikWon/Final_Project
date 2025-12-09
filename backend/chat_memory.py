# backend/chat_memory.py

class ChatMemory:
    def __init__(self):
        self.history = []
        self.last_recommendations = None
        self.last_facility = None
        self.last_mode = None

    def save_turn(self, user, ai):
        self.history.append({"user": user, "ai": ai})

    def save_recommendations(self, facility, apartments, mode):
        self.last_facility = facility
        self.last_recommendations = apartments
        self.last_mode = mode

    def get_recent_context(self):
        return {
            "last_facility": self.last_facility,
            "last_recommendations": self.last_recommendations,
            "last_mode": self.last_mode
        }

chat_memory = ChatMemory()
