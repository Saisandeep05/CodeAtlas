class Base:
    def setup(self):
        pass

class Derived(Base):
    def setup(self):
        super().setup()
