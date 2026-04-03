# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
import requests
from common import deepseek_api_key

'''
本地调用deepseek的API
'''

# 配置变量
balance_url = "https://api.deepseek.com/user/balance"
api_base_url = "https://api.deepseek.com"
model_name = "deepseek-chat"
system_message = "You are a helpful assistant"
user_message = "Hello"


def get_deepseek_balance(api_key):
    """
    查询DeepSeek账户余额
    :param api_key: DeepSeek API密钥
    :return: 返回余额信息字典
    """
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(balance_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"查询余额出错: {e}")
        return None


def call_deepseek_api():
    """
    调用DeepSeek聊天API
    :return: API响应内容
    """
    try:
        client = OpenAI(api_key=deepseek_api_key, base_url=api_base_url)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API调用失败: {e}")
        return None


def main():
    balance_info = get_deepseek_balance(deepseek_api_key)
    if not balance_info:
        return

    if balance_info.get("is_available") and \
            balance_info["balance_infos"][0]["total_balance"] > 0:
        result = call_deepseek_api()
        if result:
            print(result)
    else:
        print("账户余额不足，请充值")


if __name__ == "__main__":
    main()
