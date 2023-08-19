from langchain import OpenAI
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.tools import DuckDuckGoSearchRun, BaseTool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import StringPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
from langchain.document_loaders import UnstructuredURLLoader


from typing import Type
from pydantic import BaseModel, Field

from iso639 import Lang
import langdetect


langdetect.DetectorFactory.seed = 0

search = DuckDuckGoSearchRun()


def duck_wrapper(query, url):
    # site = "python.langchain.com"
    search_results = search.run(f"site:{url} {query}")
    return search_results


def get_site_language(url):
    loaders = UnstructuredURLLoader(urls=[url])
    data = loaders.load()
    page_content = data[0].page_content
    return langdetect.detect(page_content)


def check_languages(query, url):
    site_language = get_site_language(url)
    # site_language = langdetect.detect(url)
    user_language = langdetect.detect(query)
    if site_language != user_language:
        return True
    return False


# TODO: CRIAR UMA FUNÇÃO QUE RECONHECE A LINGUAGEM DO SITE E TRADUZ A QUERY DO USUÁRIO SE NECESSÁRIO


class AskSiteInput(BaseModel):
    """Inputs for get_current_stock_price"""

    query: str = Field(description="User query.")
    site: str = Field(description="Side to search on.")


class AskSiteTool(BaseTool):
    name = "duck_wrapper"
    description = """
        Useful when you want to know if site language is different from the user query
        language.
        """
    args_schema: Type[BaseModel] = AskSiteInput

    def _run(self, query: str, site: str):
        return check_languages(query, site)

    def _arun(self, query: str, site: str):
        raise NotImplementedError("check_languages does not support async")


# sys_msg = SystemMessage(content="""Your role is to answer the user's questions in a human-like manner using
# the tool to find the answer in the site provided by the user. You should understand what
# language the site is written and translate user question if necessary. Always give back
# the answer to the user in portuguese.""")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

tools = [AskSiteTool()]

function_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)
