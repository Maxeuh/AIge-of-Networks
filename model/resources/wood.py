from model.resources.resource import Resource


class Wood(Resource):
    """This class represents the Wood resource"""
    
    def __init__(self):
        """Initializes the wood"""
        super().__init__("Wood", "W", 100, True)