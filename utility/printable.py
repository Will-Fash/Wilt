"""Class to enable blockchain print as text, because if it outputs as objects you'll just get an object address in memory"""


class Printable:

    def __repr__(self):
        # to return it as string not dict, object as it fails if returned as a dict
        return str(self.__dict__)
