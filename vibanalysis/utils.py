
class InvalidParameter(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def integrate_acceleration_to_velocity(data, n):
    '''
    using integration to calculate velocity from acceleration,
    but to be noticed that remove the low frequency noise before utilizing 
    interation algorimth or else you'll get wrong result
    '''
    pass
