def cart_list_cache_key(user_id: int) -> str:
    return f"cart_list_user_{user_id}"