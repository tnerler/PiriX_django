# retrieve_and_generate.py
from typing_extensions import List, TypedDict
from langchain.schema import Document
from utils._faiss import build_store
from utils.load_docs import load_docs
from utils.openai_clients import get_llm
from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from sentence_transformers import CrossEncoder
from utils.chat_history_store import get_session_history
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


cross_encoder = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L-6")

class State(TypedDict):
    question: str
    context: str
    answer: str

def build_chatbot():  
    docs = load_docs()
    vector_store = build_store(docs)


    template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """
        Sen PiriX'sin, Piri Reis Üniversitesi'nin bilgi asistanısın. Temel görevin: Okul hakkında kısa, doğru ve anlaşılır bilgiler vermek.

        ÖNEMLİ KURALLAR:
        1. SADECE Piri Reis Üniversitesi konularına yanıt ver. Diğer konularda: "Ben sadece Piri Reis Üniversitesi hakkında bilgi verebilirim 💙 Diğer konular için başka bir asistana sormanı öneririm!"

        2. Bilmediğin konularda: "Bu konuda şu anda elimde bilgi yok. Detaylı bilgi için çağrı merkezimizi arayabilirsiniz: +90 216 581 00 50"

        3. Samimi ve arkadaşça konuş, robot gibi yanıtlardan kaçın. Emoji kullanabilirsin 😊

        4. Fiyat bilgilerinde şunu ekle: "Daha fazla detay için: https://aday.pirireis.edu.tr/ucretler/"

        5. Bölüm/kulüp listeleri sorulursa, verilen bilgilere sadık kalarak numaralı liste kullan. Uydurma.

        6. Okul tanıtımı sorularında güçlü yönleri vurgula ama abartma.

        7. Yanıtlar her zaman doğru, kısa ve net olmalı.

        8. 'Okulun resmi web sitesinden (https://www.pirireis.edu.tr/) ve sosyal medya hesaplarından (https://www.instagram.com/pirireisuni/) bilgi alabilirsin.' diyebilirsin.

        9. Rektör sorulursa: "Rektörü överken, onun liderlik özelliklerini ve üniversiteye katkılarını vurgula"
        """
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template(
        "Bağlam: {context}\nSoru: {question}\nCevap:"
    ),
])

    chain = template | get_llm()
    

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key = "question",
        history_messages_key = "history"
    )

    def retrieve(state: State):
        query = state["question"]
        
        # İlk aşama: Vektör veritabanından benzer dokümanları getir
        results = vector_store.similarity_search_with_score(query, k=20)
        top_docs = [doc for doc, _ in results]
        
        # İkinci aşama: Cross-encoder ile dokümanları yeniden sırala
        cross_encoder_inputs = [(query, doc.page_content) for doc in top_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)
        
        # Sonuçları skorlarına göre sırala ve en iyi 5'ini al
        reranked_docs = [
            doc for _, doc in sorted(zip(scores, top_docs), key=itemgetter(0), reverse=True)
        ][:10]

        return {
            "context": reranked_docs,
            "question": query
        }

    def generate(state: State, session_id: str):

        docs_content = "\n\n".join(doc.page_content for doc in state['context'])
        config = {"configurable": {"session_id": session_id}}

        input_data = {
            "context": docs_content,
            "question": state["question"]
        }

        answer = chain_with_history.invoke(input_data, config=config)
        

        return {"answer": answer.content}

    return retrieve, generate