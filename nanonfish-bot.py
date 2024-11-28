import asyncio
import aiohttp
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# API URLs
URLS = {
    "shop": "https://fishapi.xboost.io/zone/order/goodslist",
    "order_status": "https://fishapi.xboost.io/zone/order/status",
    "create_order": "https://fishapi.xboost.io/zone/order/createorder",
    "login": "https://fishapi.xboost.io/index/tglogin",
    "game_state": "https://fishapi.xboost.io/zone/user/gamestate",
    "game_actions": "https://fishapi.xboost.io/zone/user/gameactions",
    "task_list": "https://fishapi.xboost.io/zone/task/plist"
}

# Headers
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "origin": "https://happy-aquarium.xboost.io",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://happy-aquarium.xboost.io/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
}

# Helper function to get random colors
def get_random_color():
    colors = [Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    return random.choice(colors)

# Async HTTP POST function
async def async_post(url, headers, json=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json) as response:
            return await response.json()

# Login function
async def login(query):
    payload = {"initData": query}
    HEADERS["content-type"] = "application/json"
    try:
        response = await async_post(URLS["login"], HEADERS, json=payload)
        return response if response else None
    except Exception as e:
        print(f"{Fore.RED}Login Error: {e}{Style.RESET_ALL}")
        return None

# Fetch game state
async def load_game_state(login_token):
    HEADERS["authorization"] = login_token
    HEADERS["content-type"] = "application/json"
    try:
        response = await async_post(URLS["game_state"], HEADERS)
        return response if response else None
    except Exception as e:
        print(f"{Fore.RED}Error loading game state: {e}{Style.RESET_ALL}")
        return None

# Perform game actions (e.g., delete fish, combine fish)
async def game_action(action, fish_id, login_token):
    HEADERS["authorization"] = login_token
    HEADERS["content-type"] = "application/json"
    payload = {"actions": [{"action": action, "id": fish_id}]}
    try:
        response = await async_post(URLS["game_actions"], HEADERS, json=payload)
        return response if response else None
    except Exception as e:
        print(f"{Fore.RED}Error in game action '{action}': {e}{Style.RESET_ALL}")
        return None

# Check and create orders
async def manage_orders(goods_id, login_token):
    HEADERS["authorization"] = login_token
    HEADERS["content-type"] = "application/json"
    payload = {"goods_id": goods_id}
    try:
        create_response = await async_post(URLS["create_order"], HEADERS, json=payload)
        if create_response and create_response.get("code") == 200:
            order_no = create_response["data"]["info"]["order_no"]
            status_response = await async_post(URLS["order_status"], HEADERS, json={"order_no": order_no})
            return status_response if status_response else None
        return None
    except Exception as e:
        print(f"{Fore.RED}Error creating order: {e}{Style.RESET_ALL}")
        return None

# Main function to process accounts
async def fetch_user_data(login_token, index):
    query = login_token["query"]
    token = login_token["login_token"]
    color = get_random_color()

    # Load game state
    game_state = await load_game_state(token)
    if game_state and game_state.get("code") == 200:
        data = game_state["data"]
        fishes = data["fishes"]
        gold = data["gold"]
        level = data["level"]
        fish_limit = data["fishLimit"]

        result = (
            f"Akun {color}{index + 1}{Style.RESET_ALL} | "
            f"Level: {color}{level}{Style.RESET_ALL} | "
            f"Gold: {color}{gold}{Style.RESET_ALL} | "
            f"Fish Limit: {color}{fish_limit}{Style.RESET_ALL} | "
            f"Fishes: {color}{fishes}{Style.RESET_ALL}"
        )
        return result
    else:
        return f"{Fore.RED}Failed to fetch user data for Akun {index + 1}{Style.RESET_ALL}"

# Main function
async def main():
    init(autoreset=True)
    print(f"{Fore.GREEN}Starting Fish Bot...{Style.RESET_ALL}")
    
    with open("query.txt", "r") as file:
        queries = file.read().splitlines()

    login_tokens = []
    for query in queries:
        login_response = await login(query)
        if login_response and login_response.get("code") == 200:
            login_tokens.append({
                "query": query,
                "login_token": login_response["data"]["login_token"]
            })
        else:
            print(f"{Fore.RED}Login failed for query: {query}{Style.RESET_ALL}")

    while True:
        tasks = [fetch_user_data(token, idx) for idx, token in enumerate(login_tokens)]
        results = await asyncio.gather(*tasks)

        # Print results
        print("\033c", end="")  # Clear terminal
        print("\n".join(results))

        # Wait before next cycle
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
