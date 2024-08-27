from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class State(TypedDict):
    # Annotating our messages list with the add_messages function instructs Python to always append new messages to the existing list.
    messages: Annotated[list[AnyMessage], add_messages]
    
    # Similarly, annotating dialog_state with the update_dialog_stack function instructs Python to call update_dialog_stack whenever a new dialog_state is returned by some Node.
    dialog_state: Annotated[
        list[str],
        update_dialog_stack,
    ]