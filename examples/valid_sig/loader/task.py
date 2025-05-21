class Task:
    def __init__(self, title: str, completed: bool):
        self.title = title
        self.completed = completed
    
    def __repr__(self):
        return f"Task title: {self.title}, completed: {self.completed}"
