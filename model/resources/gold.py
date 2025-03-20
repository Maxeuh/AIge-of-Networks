from model.resources.resource import Resource


class Gold(Resource):
    """This class represents the Gold resource"""
    
    def __init__(self):
        """Initializes the gold"""
        super().__init__("Gold", "G", 800, True)