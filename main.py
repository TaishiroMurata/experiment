import os
from google.cloud import secretmanager
from google.cloud import bigquery
from openai import AzureOpenAI
import openai

def return_hello():
    return "Hello"

def run_bigquery_query():
    
    """BigQueryでクエリを実行し、結果を表示する関数"""
    client = bigquery.Client()
    query = """
    SELECT title, category
    FROM `zuu-infra.prd_to_articles.to_article_urls`
    ORDER BY title DESC
    LIMIT 5;
    """
    query_job = client.query(query)
    results_list = [{ "title": row['title'], "category": row['category']} for row in query_job]
    print(results_list)
    return results_list

def interact_with_openai(results_list):
    # Azure OpenAI クライアントの初期化

    name = f"projects/zuu-infra/secrets/my-secret/versions/3"

    # シークレットのバージョンを取得
    response = client.access_secret_version(request={"name": name})
    secret_value = response.payload.data.decode("UTF-8")

    client = AzureOpenAI(
        azure_endpoint="https://zuu-pdev-us2.openai.azure.com/",
        api_key=secret_value,
        api_version="2024-02-15-preview"
    )

    # OpenAIに送るシステムメッセージで、リスト内のtitleだけを取り出すように指示
    message_text = [
        {"role": "system", "content": "Given the following data, extract only the titles and return them as an array."},
        {"role": "user", "content": str(results_list)}
    ]

    # OpenAI APIを呼び出し
    completion = client.chat.completions.create(
        model="gpt4-turbo-saino01",  # モデル名はデプロイメント名に置き換え
        messages=message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    return completion['choices'][0]['text']

def main(request):
    # BigQueryでクエリを実行
    bigquery = run_bigquery_query()
    # OpenAIによるデータ処理
    #interact_with_openai(results)
    return "エラーなく完了しました。"