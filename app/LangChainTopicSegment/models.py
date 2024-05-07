import langchain
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from langchain_core.documents.base import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import List
import re,os,json, logging,tiktoken


class LoadDocument:
    def __init__(self, path):
        self.logger = logging.getLogger(__name__)
        self.path = path

    def load(self):
        self.logger.debug(f"Loading documents from {self.path}")
        text_loader_kwargs = {'autodetect_encoding': True}
        loader = DirectoryLoader(self.path, show_progress=True,
                                 loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)

        return loader.load()

class TVNewsIdentifier(BaseModel):
    doc_id: int = Field(description="doc_id from the input parameters")
    category: str = Field(description="The category of the topic, the same category has the same words, for example Politics, Sports, Justice, etc.")
    topic: str = Field(description="The main topic identified, like the header of the news, the same topic has the same words")
    subtopic: str = Field(description="The more concise topic identified, like the subheader of the news, the same subtopic has the same words")

class TopicIdentifier:
    def __init__(self,model="gpt-4-1106-preview"):
        self.logger = logging.getLogger(__name__)
        self.chat = ChatOpenAI(temperature=0.0,model=model,openai_api_key=os.environ.get("OPENAI_API_KEY"))
        self.output_parser = PydanticOutputParser(pydantic_object=TVNewsIdentifier)
        self.format_instructions = self.output_parser.get_format_instructions()
        self.tiktoken_encoding = tiktoken.get_encoding("cl100k_base")
        self.tiktoken_encoding_model = tiktoken.encoding_for_model(model)

    def get_topic_assigment_template(self):
        topic_assigment_msg = '''
        Below is a list of news, segmented from a TV news program. Is in JSON format with the following keys:
        1. doc_id: The id of the document
        2. news: The content to identify a topic
        
        Identify the main topic for each document, each document 
        has different content and the topics may be different, all the news belong
        to a complete TV news which explains a set of different topics. Provide 
        the key words for each topic and use the same key words for the same topic 
        
        Provide the result with a JSON format exactly with the following structure:
        {format_instructions}
        
        
        TV news documents:
        {input_data}
        '''

        return ChatPromptTemplate.from_messages([
            ("system", "You're a helpful assistant. Your task is to identify news and the topic they contain."),
            ("human", topic_assigment_msg)
        ])

    def prepare_promtp(self,docs_batch_data):
        self.logger.debug(f"Preparing prompt for {len(docs_batch_data)} documents")
        topic_assignment_template = self.get_topic_assigment_template()
        self.logger.debug(f"Prompt prepared, creating message")
        messages = topic_assignment_template.format_messages(
            format_instructions=self.format_instructions,
            input_data=json.dumps(docs_batch_data)
        )
        self.logger.debug(f"Message created, returning messages")
        return messages

    def get_docs_batch_data(self,docs):
        self.logger.debug(f"Loading {len(docs)} documents")
        docs_batch_data = []
        for doc in docs:
            docs_batch_data.append({
                "doc_id": doc.metadata['id'],
                "news": doc.page_content
            })
        self.logger.debug(f"Loaded {len(docs_batch_data)} documents")
        return docs_batch_data

    def run(self,docs:list[Document]):
        self.logger.info(f"Starting topic identification for {len(docs)} documents")
        docs_batch_data = self.get_docs_batch_data(docs)

        self.logger.info(f"Created batch docs")
        messages = self.prepare_promtp(docs_batch_data)

        tokens = len(self.tiktoken_encoding.encode(' '.join([x.content for x in messages])))
        self.logger.info(f"Prepared prompt of {tokens} tokens")
        if tokens > 127999:
            raise Exception(f"Prompt too long, {tokens} tokens, maximum 127999 tokens")
        response = self.chat(messages)
        self.logger.info(f"Got response,{response.response_metadata}")

        patron = r"\[(.*?)\]"
        resp = re.findall(patron, response.content,re.DOTALL)
        resp = list(list(map(lambda x: eval(x.replace('\n','')),
                                 resp))[0])

        self.logger.info(f"Response parsed")
        self.logger.info(f"Topic identification finished")
        return docs_batch_data,resp

    def run_chain(self,docs:list[Document]):
        #TOREIMPLEMENT
        return None
        docs_batch_data = self.get_docs_batch_data(docs)
        messages = self.prepare_promtp(docs_batch_data)
        chain = LLMChain(llm=self.chat, prompt=self.get_topic_assigment_template(),
                         )
        response = chain.run(
            format_instructions=self.format_instructions,
            input_data=json.dumps(docs_batch_data)
        )
        patron = r"\[(.*?)\]"
        resp =re.findall(patron, response.content)

        return list(map(lambda x: self.output_parser.parse(x),
                                 resp))

    def run_seq_chain(self,docs:list[Document]):
        #TOREIMPLEMENT
        return None
        chain = self.get_topic_assigment_template() | self.chat
        response = chain.invoke(
            {
                "format_instructions": self.format_instructions,
                "input_data": json.dumps(self.get_docs_batch_data(docs))
            }
        )

class TextSegmenter:
    def __init__(self, text:str,openai_api_key:str=None):
        self.logger = logging.getLogger(__name__)
        self.text = self.preprocess_text(text)
        self.text_splitter = SemanticChunker(OpenAIEmbeddings())


    def preprocess_text(self,texto):
        self.logger.debug(f"Preprocessing text")
        texto_limpio = re.sub(r'[\xc2\xa0\t\n]+', ' ', texto)
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
        texto_limpio = texto_limpio.strip()
        self.logger.debug(f"Text preprocessed")
        return texto_limpio

    def split(self) -> [Document]:
        self.logger.debug(f"Splitting text")
        splits = self.text_splitter.create_documents([self.text])
        for i in range(len(splits)):
            splits[i].metadata['id'] = i
        self.logger.debug(f"Text splitted")
        return splits


def Processer(text:str,debug:bool=True,openai_api_key:str=None):
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    logger = logging.getLogger(__name__)
    logger.info(f"Starting processer")
    langchain.debug = debug
    splitter = TextSegmenter(text)
    splits = splitter.split()
    logger.info(f"Text splitted into {len(splits)} documents")
    topic_identifier = TopicIdentifier()
    logger.info(f"Starting topic identification")
    return topic_identifier.run(splits)



class DocumentUnifier:
    def __init__(self,docs_batch_data,resp):
        self.docs_batch_data = docs_batch_data
        self.resp = resp


    def unify_by_category(self):
        docs_by_category = {}
        for doc,resp in zip(self.docs_batch_data,self.resp):
            if resp['category'] not in docs_by_category:
                docs_by_category[resp['category']] = []
            docs_by_category[resp['category']].append({
                "doc_id": doc['doc_id'],
                "news": doc['news']
            })
        return docs_by_category

    def unify_by_topic(self):
        docs_by_topic = {}
        for doc,resp in zip(self.docs_batch_data,self.resp):
            if resp['topic'] not in docs_by_topic:
                docs_by_topic[resp['topic']] = []
            docs_by_topic[resp['topic']].append({
                "doc_id": doc['doc_id'],
                "news": doc['news']
            })
        return docs_by_topic

    def unify_by_subtopic(self):
        docs_by_subtopic = {}
        for doc,resp in zip(self.docs_batch_data,self.resp):
            if resp['subtopic'] not in docs_by_subtopic:
                docs_by_subtopic[resp['subtopic']] = []
            docs_by_subtopic[resp['subtopic']].append({
                "doc_id": doc['doc_id'],
                "news": doc['news']
            })
        return docs_by_subtopic

