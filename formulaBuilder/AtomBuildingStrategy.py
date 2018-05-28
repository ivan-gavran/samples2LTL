from enum import IntEnum
class AtomBuildingStrategy(IntEnum):
    RANDOM_SAMPLING = 0
    BOOST_MISCLASSIFIED = 1
    CHOOSE_NOT_SEPARATED = 2
    
    
