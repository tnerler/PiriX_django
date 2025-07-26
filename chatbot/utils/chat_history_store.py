from langchain_community.chat_message_histories import ChatMessageHistory
import threading

# Thread-safe store
store = {}
store_lock = threading.Lock()

def get_session_history(session_id: str) -> ChatMessageHistory:
    with store_lock:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

def clear_session_history(session_id: str):
    """Session history'yi temizle"""
    with store_lock:
        if session_id in store:
            del store[session_id]

def get_all_sessions():
    """Debug için tüm session'ları listele"""
    with store_lock:
        return list(store.keys())