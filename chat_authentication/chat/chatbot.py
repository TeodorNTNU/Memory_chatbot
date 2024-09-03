import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from .custom_chat_history import DjangoChatMessageHistory
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_astradb import AstraDBVectorStore
from astrapy import DataAPIClient
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ASTRA_TOKEN = os.getenv('ASTRA_TOKEN')
ASTRA_ENDPOINT = os.getenv('ASTRA_ENDPOINT')
ASTRA_NAMESPACE = os.getenv('ASTRA_NAMESPACE')

COLLECTION = 'text_qa_pdf'

load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, streaming=True)


embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

client = DataAPIClient(ASTRA_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_ENDPOINT, namespace=ASTRA_NAMESPACE)

vstore = AstraDBVectorStore(
    embedding=embedding,
    namespace=ASTRA_NAMESPACE,
    collection_name=COLLECTION,
    token=ASTRA_TOKEN,
    api_endpoint=ASTRA_ENDPOINT
)

# Define the retriever with similarity search
retriever = vstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.5},
)


contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

########### RAG PROMPT ###############

# Incorporate the retriever into a question-answering chain.
rag_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}
"""
rag_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", rag_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

######### CHAT PROMPT ###########

# Incorporate the retriever into a question-answering chain.
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You're an assistant knowledgeable in AI and algorithms. Answer clearly and concisely."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])


# now initialize the conversation chain
runnable = prompt_template | llm

question_answer_chain = create_stuff_documents_chain(llm, rag_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)



from .custom_chat_history import DjangoChatMessageHistory

def get_session_history(session_id):
    """
    Retrieves the message history for a given session ID.
    """
    try:
        # Make sure `session_id` is converted to integer if required
        conversation_id = int(session_id)  # Ensure that session_id is correctly converted or used
        return DjangoChatMessageHistory(conversation_id=conversation_id)
    except ValueError:
        raise ValueError(f"Invalid session ID format: {session_id}")


runnable_with_history = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
    #output_messages_key="answer",
)


