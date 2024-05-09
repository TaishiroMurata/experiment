import os
from google.cloud import secretmanager
from google.cloud import bigquery
from openai import AzureOpenAI
import openai

#bigqueyからデータを引っ張ってくる
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

#取得したデータをAzureのOpenAIサービスに投げる
def interact_with_openai(results_list):

    #シークレットマネージャーの取得
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/zuu-infra/secrets/my-secret/versions/3"
    
    # シークレットのバージョンを取得
    response = client.access_secret_version(request={"name": name})
    secret_value = response.payload.data.decode("UTF-8")

    azure_client = AzureOpenAI(
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
    response = azure_client.chat.completions.create(
        model="gpt4-turbo-saino01",  # モデル名はデプロイメント名に置き換え
        messages=message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    print(response.model_dump_json(indent=2))

    return response.model_dump_json(indent=2)

#それをbigqueryに投げてテーブルの作成をする
def return_to_bigquey(api_answer):

    client = bigquery.Client()

    # データセットの設定
    dataset_id = "{}.my_new_dataset".format(client.project)
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "asia-northeast1"

    # データセットの作成
    dataset = client.create_dataset(dataset, timeout=30)
    print("Created dataset {}.{}".format(client.project, dataset.dataset_id))

    # テーブルの設定
    table_id = "{}.{}.my_new_table".format(client.project, dataset.dataset_id)
    schema = [
        bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category", "STRING", mode="REQUIRED"),  # データ型をSTRINGに修正
    ]
    table = bigquery.Table(table_id, schema=schema)

    # テーブルの作成
    table = client.create_table(table)
    print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))

    #取得したデータをテーブルに挿入するデータに挿入する
    rows_to_insert = api_answer

    # データの挿入
    errors = client.insert_rows_json(table, rows_to_insert)
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors)) 

def main(request):

    # BigQueryでクエリを実行
    bigquery = run_bigquery_query()

    # OpenAIによるデータ処理
    answer = interact_with_openai(bigquery)

    #bigqueryにデータを返す
    return_to_bigquey(answer)

    return "エラーなく完了しました。"