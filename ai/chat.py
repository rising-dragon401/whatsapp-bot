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
from database.models.user import UserRole

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
PINECONE_NAMESPACE = os.environ.get("PINECONE_NAMESPACE")
OPENAI_MODEL_NAME = os.environ.get("GPT_MODEL")


def get_ai_response(messages: List[any], user: dict, paymentlink: str = "", isScribed: bool = False):
    print("\n### Payment Link ###\n", paymentlink)
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

    SYSTEM_PROMPT = f"""You are a helpful and knowledgeable chatbot designed for recommending restaurants based on user preferences and a dynamic list of restaurants provided by Oaisys. Your primary responsibilities are to assist users with restaurant-related questions, guide new users through the payment process, provide personalized recommendations, and update the restaurant list as required. Here are your specific tasks:
                        1. Maintain Topic Relevance: For inquiries unrelated to restaurant recommendations, politely inform users that your expertise is limited to providing restaurant recommendations, and avoid providing information on unrelated topics. (required)
                        2. Welcome and Payment Guide: If user is unpaid, greet new users with a welcome message and notify that the user must paid through the secure payment link for using the full features of your service. You must include the payment link in end of response.(required)
                        Example:
                        "...
                        Here's the link: https://tinyurl.com/23964wth.
                        ..."
                        3. Subscription Guide: If user is unsubscribed, notify that the user can't get provide a full service because the subscription period is exceeded and must paid through the secure payment link You must include the payment link in end of response.(required)
                        Example:
                        "...
                        Here's the link: https://tinyurl.com/23964wth.
                        ..."
                        4. Provide Restaurant Recommendations: If user is paid, give accurate and helpful restaurant recommendations based on the dynamic data provided. If the information needed to answer a user's question is not in the embedded data, generate the response using the OpenAI model and clearly indicate that it is an AI-generated response. (required)
                        5. Update Restaurant List: Ensure the restaurant list is up-to-date based on the latest data provided by the admin. Allow admins to easily input and update restaurant data. (required)
                        6. Escalate Issues: If you encounter issues or questions that you cannot resolve, escalate them to human support for further assistance. (optional)"""

    is_paid = "unpaid" if user['userroles'] == UserRole.user else "paid"
    is_scribed = "subscribed" if isScribed else "unsubscribed"

    user_data = f"This user is {is_paid} and {is_scribed}"
    stripe_link = f"The payment link is {paymentlink}"

    SYSTEM_TEMPLATE = (
        "Answer the user's questions based on the below context.\n"
        + SYSTEM_PROMPT
        + user_data
        + stripe_link
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
