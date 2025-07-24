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

cross_encoder = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L-6")

class State(TypedDict):
    question: str
    context: str
    answer: str

def build_chatbot():  
    docs = load_docs()
    vector_store = build_store(docs)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key='question',
        output_key="answer"
    )

    template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """
        Sen PiriX'sin, Piri Reis Üniversitesi'nin bilgi asistanısın. Temel görevin: Okul hakkında kısa, doğru ve anlaşılır bilgiler vermek.

        ÖNEMLİ KURALLAR:
        1. SADECE Piri Reis Üniversitesi konularına yanıt ver. Diğer konularda: "Ben sadece Piri Reis Üniversitesi hakkında bilgi verebilirim 💙 Diğer konular için başka bir asistana sormanı öneririm!"

        2. Bilmediğin konularda: "Bu konuda şu anda elimde bilgi yok. Detaylı bilgi için çağrı merkezimizi arayabilirsiniz: +90 216 581 00 50"

        3. Samimi ve arkadaşça konuş, robot gibi yanıtlardan kaçın. Emoji kullanabilirsin 😊

        4. Fiyat bilgilerinde her zaman "2025-2026 yılı ücretleri" olduğunu belirt ve şunu ekle: "Daha fazla detay için: https://aday.pirireis.edu.tr/ucretler/"

        5. Bölüm/kulüp listeleri sorulursa, verilen bilgilere sadık kalarak numaralı liste kullan. Uydurma.

        6. Okul tanıtımı sorularında güçlü yönleri vurgula ama abartma.

        7. Yanıtlar her zaman doğru, kısa ve net olmalı.
        """
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template(
        "Bağlam: {context}\nSoru: {question}\nCevap:"
    ),
])

    chain = template | get_llm()

    def retrieve(state: State):
        query = state["question"]
        
        # İlk aşama: Vektör veritabanından benzer dokümanları getir
        results = vector_store.similarity_search_with_score(query, k=10)
        top_docs = [doc for doc, _ in results]
        
        # İkinci aşama: Cross-encoder ile dokümanları yeniden sırala
        cross_encoder_inputs = [(query, doc.page_content) for doc in top_docs]
        scores = cross_encoder.predict(cross_encoder_inputs)
        
        # Sonuçları skorlarına göre sırala ve en iyi 5'ini al
        reranked_docs = [
            doc for _, doc in sorted(zip(scores, top_docs), key=itemgetter(0), reverse=True)
        ][:5]

        return {
            "context": reranked_docs,
            "question": query
        }

    def generate(state: State):
        if not state["context"]:
            return {"answer": "Bu konuda şu anda elimde bilgi yok. Detaylı bilgi için çağrı merkezimizi arayabilirsiniz: +90 216 581 00 50"}

        docs_content = "\n\n".join(doc.page_content for doc in state['context'])
        chat_history = memory.load_memory_variables({}).get("chat_history", [])

        input_data = {
            "context": docs_content,
            "question": state["question"],
            "chat_history": chat_history
        }

        answer = chain.invoke(input_data)
        memory.save_context({"question": state["question"]}, {"answer": answer.content})

        return {"answer": answer.content}

    return retrieve, generate