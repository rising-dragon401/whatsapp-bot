from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CONFIG
import time

def initate_indexs():
    pc = Pinecone(api_key=CONFIG.pinecone_api_key)

    index_name = CONFIG.pinecone_index
    namespace = CONFIG.pinecone_namespace

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name in existing_indexes:
        pc.delete_index(index_name)

def embedding_pdf_file(pathname: str):
    print("\n***** Starting Embedding *****\n")
    loader = PyPDFLoader(pathname, extract_images=True)
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=60, separators=[
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
        "",
        "@ ",
        "# ",
        "- ",
        "* ",
        "** ",
        "(a)",
        "(b)",
        "(c)",
        "(d)",
        "(e)",
        "(e)",
        "(f)",
        "(g)",
        "(h)",
        "---",
        "1.",
        "2.",
        "3.",
        "4.",
        "5.",
        "6.",
        "7.",
        "8.",
        "9.",
        "10.",
        "12.",
        "13.",
        "14.",
        "15.",
        "16.",
        "17.",
        "18.",
        "19.",
        "20.",
        "21.",
        "22.",
        "23.",
        "24.",
        "25.",
        "26.",
        "27.",
        "28.",
        "29.",
        "30.",
    ])

    pages = loader.load_and_split(text_splitter=splitter)
    
    print("pages len", len(pages))

    embeddings_model = OpenAIEmbeddings(openai_api_key=CONFIG.openai_api_key)
    # embeddings = embeddings_model.embed_documents(texts=csv_data)

    
    pc = Pinecone(api_key=CONFIG.pinecone_api_key)

    index_name = CONFIG.pinecone_index
    namespace = CONFIG.pinecone_namespace

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pc.Index(index_name)

    # The OpenAI embedding model `text-embedding-ada-002 uses 1536 dimensions`
    docsearch = PineconeVectorStore.from_documents(
        pages,
        embeddings_model,
        index_name=index_name,
        namespace=namespace,
    )