class Service:
    @property
    def status(self):
        return "active"

    @staticmethod
    def helper():
        pass

def run():
    Service.helper()
