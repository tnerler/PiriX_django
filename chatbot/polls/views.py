from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from .models import ChatLog, FeedBack
import logging
from utils.chat_history_store import get_session_history
from utils.retrieve_and_generate import build_chatbot
import uuid
import time

# Logger ekleyelim debug için
logger = logging.getLogger(__name__)

def home(request):
    return render(request, "index.html")

retrieve, generate = build_chatbot()

@csrf_exempt
@require_http_methods(["POST"])
def ask(request):
    try:
        data = json.loads(request.body)
        question = data.get("question", "")
        session_id = data.get("session_id") or request.COOKIES.get("session_id")

        if not session_id:
            session_id = str(uuid.uuid4())

        if not question:
            return JsonResponse({"error": "Soru bos olamaz."}, status=400)
        
        
        # Chat history'yi kontrol et
        history = get_session_history(session_id)
        
        
        # State oluştur
        state = {
            "question": question,
            "context": [],
            "answer": ""
        }

        # Retrieve yap
        retrieval_result = retrieve(state, session_id=session_id)
        state["context"] = retrieval_result["context"]

        # Generate yap - bu otomatik olarak history'ye ekleyecek
        generation_result = generate(state, session_id=session_id)
        


        user = request.user if request.user.is_authenticated else None

        # Database'e kaydet
        chatlog = ChatLog.objects.create(
            user=user,
            question=question,
            answer=generation_result["answer"],
            session_id=session_id
        )


        # Response oluştur
        response = JsonResponse({
            "answer": generation_result["answer"],
            "feedback_id": chatlog.id,
            "session_id": session_id  # Debug için
        })
        
        # Cookie ayarla
        if not request.COOKIES.get("session_id"):
            response.set_cookie("session_id", session_id, max_age=30*24*60*60)
            
        return response

    except Exception as e:
        logger.error(f"Ask endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def feedback(request):
    try:
        logger.info(f"Feedback request body: {request.body}")
        
        data = json.loads(request.body)
        feedback_id = data.get("feedback_id")
        feedback_type = data.get("feedback_type")
        session_id = data.get("session_id") or request.COOKIES.get("session_id")

        logger.info(f"Feedback ID: {feedback_id}, Feedback Type: {feedback_type}")

        if not feedback_id:
            return JsonResponse({"error": "Feedback ID gerekli."}, status=400)

        if feedback_type not in ("like", "dislike"):
            return JsonResponse({"error": "Geçersiz feedback türü."}, status=400)

        user = request.user if request.user.is_authenticated else None

        try:
            chatlog = ChatLog.objects.get(id=feedback_id)
            logger.info(f"ChatLog bulundu: {chatlog}")
        except ChatLog.DoesNotExist:
            logger.error(f"ChatLog bulunamadı: {feedback_id}")
            return JsonResponse({"error": "ChatLog not found"}, status=404)

        feedback_obj, created = FeedBack.objects.update_or_create(
            chatlog=chatlog,
            user=user,
            defaults={"feedback_type": feedback_type, "session_id": session_id}
        )
        
        logger.info(f"Feedback {'created' if created else 'updated'}: {feedback_obj}")

        return JsonResponse({
            "status": "success",
            "created": created,
            "feedback_id": feedback_obj.id
        })
    
    except Exception as e:
        logger.error(f"Feedback endpoint error: {str(e)}")
        return JsonResponse({"error": f"Bir hata oluştu: {str(e)}"}, status=500)