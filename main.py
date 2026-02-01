from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Create LLM
llm = ChatOpenAI()

# Create prompt template
prompt = ChatPromptTemplate([
    ("system", "You are a professional {domain} expert"),
    ("human", "Please explain the concept and applications of {topic}")
])

# Create chain
chain = prompt | llm  # pyright: ignore[reportUnknownVariableType]

# Invoke chain
response = chain.invoke({  # pyright: ignore[reportUnknownMemberType]
    "domain": "machine learning",
    "topic": "deep learning"
})

print(response.content)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]