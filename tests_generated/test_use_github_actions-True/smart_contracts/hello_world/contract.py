from algopy import (
    ARC4Contract,
    arc4,
)


class HelloWorldApp(ARC4Contract):
    def clear_state_program(self) -> bool:
        return True

    @arc4.abimethod()
    def hello(self) -> arc4.String:
        return arc4.String("Hello World!")
