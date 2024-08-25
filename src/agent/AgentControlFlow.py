from langchain_core.pydantic_v1 import BaseModel, Field

class CompleteTask(BaseModel):
    """A tool to mark the current task as completed."""
    cancel: bool = False

class ToInternalSearchAgent(BaseModel):
    """Call on the internal search agent."""
    instruction: str = Field(
        description = "Instructions for the internal search agent on exactly what to search for."
    )

class ToExternalSearchAgent(BaseModel):
    """Call on the external search agent."""
    instruction: str = Field(
        description = "Instructions for the external search agent on exactly what to search for."
    )

class ToWriterAgent(BaseModel):
    """Call on the writer agent."""
    instruction: str = Field(
        description = "Description of what the writer agent should produce, as well as any specific content, template or formatting requirements."
    )