from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage


class BaseChatModelExtensions:
    def __init__(self, llm: BaseChatModel) -> None:
        super().__init__()
        self._llm = llm

    def summarize(self, text: str) -> AIMessage:
        prompt = f"""
        Summarize the following text:
        {text}
        """
        result = self._llm.invoke(prompt)

        return result
