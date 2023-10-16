import os
from langchain.prompts import ChatPromptTemplate
# from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatLiteLLM as ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from agent.prompts import generate_report_prompt, generate_agent_role_prompt
from config import Config

CFG = Config()

class WriterActor:
    def __init__(self):
        self.model = ChatOpenAI(model=CFG.smart_llm_model, 
                                model_kwargs={"api_version": os.getenv("AZURE_API_VERSION", "2023-07-01-preview"),
                                              "api_type": os.getenv("API_TYPE", "azure")
                                              })
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", generate_agent_role_prompt(agent="Default Agent")),
            ("user", generate_report_prompt(question="{query}", research_summary="{results}"))
        ])

    @property
    def runnable(self):
        return {
            "answer": {
                "query": lambda x: x["query"],
                "results": lambda x: "\n\n".join(x["results"])
              } | self.prompt | self.model | StrOutputParser()
        }
