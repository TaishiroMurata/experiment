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
    completion = azure_client.chat.completions.create(
        model="gpt4-turbo-saino01",  # モデル名はデプロイメント名に置き換え
        messages=message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    print(response.choices[0].message.content)

    return response.choices[0].message.contentx


""" ChatCompletion(
    id='chatcmpl-9MqfHhF63d0AGWLG7ALDzG12ZGUVI', 
    choices=[
        Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage
               (content='The extracted titles from the given data are as follows:\n\n```json\n[\n    "｢シンプルセレクト型規格住宅｣のFC加盟支援事業を開始・住宅業界の新しいスタンダード｢QOL住宅｣の普及へ",\n    "～脱フロンに向けて～、味の素冷凍食品やニチレイフーズ・テーブルマークが取り組み〈冷凍食品業界の状況〉",\n    "～相続登記編～\\u3000登記識別情報",\n    "～相続登記編～\\u3000登記事項証明書",\n    "～相続登記編～\\u3000固定資産評価証明書"\n]\n```', 
                role='assistant', 
                function_call=None, 
                tool_calls=None), 
                content_filter_results={'hate': {'filtered': False, 'severity': 'safe'}, 'self_harm': {'filtered': False, 'severity': 'safe'}, 'sexual': {'filtered': False, 'severity': 'safe'}, 'violence': {'filtered': False, 'severity': 'safe'}})], 
                created=1715232687, 
                model='gpt-4', 
                object='chat.completion', 
                system_fingerprint='fp_2f57f81c11', 
                usage=CompletionUsage(
                    completion_tokens=235, 
                    prompt_tokens=292, 
                    total_tokens=527), 
                prompt_filter_results=[{'prompt_index': 0, 'content_filter_results': {'hate': {'filtered': False, 'severity': 'safe'}, 'self_harm': {'filtered': False, 'severity': 'safe'}, 'sexual': {'filtered': False, 'severity': 'safe'}, 'violence': {'filtered': False, 'severity': 'safe'}}}])
 """