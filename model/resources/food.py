from model.resources.resource import Resource


class Food(Resource):
    """This class represents the Food resource"""
    
    def __init__(self):
        """Initializes the food"""
        super().__init__("Food", "F", 300, False)