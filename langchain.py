from langchain import LLMClient
from langchain.schema import Message
from langchain.clients import LangChainClient

# LangChain API キーとエンドポイントの設定
api_key = "YOUR_LANGCHAIN_API_KEY"
endpoint = "https://api.langchain.com"

# LLMClientの初期化
llm_client = LLMClient(
    api_key=api_key,
    endpoint=endpoint
)

# LangChainClientの初期化
langchain_client = LangChainClient(llm_client=llm_client)

# システムとユーザーメッセージを設定
messages = [
    Message(role="system", content="Given the following data, extract only the titles and return them as an array."),
    Message(role="user", content=str("変数"))
]

# LangChain APIを呼び出し
response = langchain_client.get_response(
    messages=messages,
    model_name="gpt4-turbo-saino01",  # モデル名を適切なものに変更してください
    temperature=0.7,
    max_tokens=800,
    top_p=0.95
)
# return text
