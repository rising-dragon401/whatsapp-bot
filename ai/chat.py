import os
from pinecone import Pinecone

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
PINECONE_NAMESPACE = os.environ.get("PINECONE_NAMESPACE")
OPENAI_MODEL_NAME = os.environ.get("GPT_MODEL")


def get_ai_response(messages: List[any]):
    chat = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model=OPENAI_MODEL_NAME,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )

    pc = Pinecone(api_key=PINECONE_KEY)
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    index = pc.describe_index(PINECONE_INDEX)

    pinecone_namespace = PINECONE_NAMESPACE

    print("pinecone_namespace", pinecone_namespace)

    SYSTEM_PROMPT = f"""You are a helpful and knowledgeable chatbot designed for recommending restaurants based on user preferences and a dynamic list of
                        restaurants provided by Oaisys. Your primary responsibilities are to assist users with restaurant-related questions, guide new users through the payment process, provide personalized recommendations, and update the restaurant list as required. Here are your specific tasks:
                        1. Maintain Topic Relevance: For inquiries unrelated to restaurant recommendations, politely inform users that your expertise is limited to providing restaurant recommendations, and avoid providing information on unrelated topics. (required)
                        2. Welcome and Payment Guide: Greet new users with a welcome message and guide them through the payment process to access full features. Use the Stripe API to generate and send secure payment links. (required)
                        3. Provide Restaurant Recommendations: Give accurate and helpful restaurant recommendations based on the dynamic data provided. If the information needed to answer a user's question is not in the embedded data, generate the response using the OpenAI model and clearly indicate that it is an AI-generated response. (required)
                        4. Update Restaurant List: Ensure the restaurant list is up-to-date based on the latest data provided by the admin. Allow admins to easily input and update restaurant data. (required)
                        5. Escalate Issues: If you encounter issues or questions that you cannot resolve, escalate them to human support for further assistance. (optional)"""

    SYSTEM_TEMPLATE = (
        "Answer the user's questions based on the below context.\n"
        + SYSTEM_PROMPT
        + """ 
        <context>
        {context}
        </context>
    """
    )
    vectorstore = PineconeVectorStore(
        pinecone_api_key=PINECONE_KEY,
        index_name=PINECONE_INDEX,
        embedding=embeddings,
        namespace=pinecone_namespace,
    )
    retriever = vectorstore.as_retriever()

    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_TEMPLATE,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    document_chain = create_stuff_documents_chain(chat, question_answering_prompt)

    query_transform_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant "
                "to the conversation. Only respond with the query, nothing else.",
            ),
        ]
    )

    query_transforming_retriever_chain = RunnableBranch(
        (
            lambda x: len(x.get("messages", [])) == 1,
            # If only one message, then we just pass that message's content to retriever
            (lambda x: x["messages"][-1].content) | retriever,
        ),
        # If messages, then we pass inputs to LLM chain to transform the query, then pass to retriever
        query_transform_prompt | chat | StrOutputParser() | retriever,
    ).with_config(run_name="chat_retriever_chain")

    conversational_retrieval_chain = RunnablePassthrough.assign(
        context=query_transforming_retriever_chain,
    ).assign(
        answer=document_chain,
    )

    history = []
    for item in messages:
        if item["role"] == "system":
            history.append(SystemMessage(content=item["content"]))
        if item["role"] == "user":
            history.append(HumanMessage(content=item["content"]))
        if item["role"] == "assistant":
            history.append(AIMessage(content=item["content"]))

    response = conversational_retrieval_chain.invoke(
        {
            "messages": history,
        }
    )

    return response["answer"]
