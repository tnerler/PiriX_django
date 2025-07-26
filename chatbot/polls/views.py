from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from .models import ChatLog, FeedBack
import logging

from utils.retrieve_and_generate import build_chatbot
import uuid

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
        
        state = {
            "question": question,
            "context": [],
            "answer": ""
        }

        retrieval_result = retrieve(state)
        state["context"] = retrieval_result["context"]

        generation_result = generate(state, session_id=session_id)

        user = request.user if request.user.is_authenticated else None

        chatlog = ChatLog.objects.create(
            user=user,
            question=question,
            answer=generation_result["answer"],
            session_id = session_id
        )

        # Set cookie if not present
        response = JsonResponse({
            "answer": generation_result["answer"],
            "feedback_id": chatlog.id
        })
        if not request.COOKIES.get("session_id"):
            response.set_cookie("session_id", session_id, max_age=30*24*60*60)
        return response

    except Exception as e:
        logger.error(f"Ask endpoint error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
@require_http_methods(["POST"])
def feedback(request):
    try:
        # Debug için request body'yi loglayalım
        logger.info(f"Feedback request body: {request.body}")
        
        data = json.loads(request.body)
        # Changed: Look for feedback_id instead of chatlog_id to match frontend
        feedback_id = data.get("feedback_id")
        feedback_type = data.get("feedback_type")


        session_id = data.get("session_id") or request.COOKIES.get("session_id")

        # Debug için gelen değerleri loglayalım
        logger.info(f"Feedback ID: {feedback_id}, Feedback Type: {feedback_type}")

        # Validation checks
        if not feedback_id:
            return JsonResponse({"error": "Feedback ID gerekli."}, status=400)

        if feedback_type not in ("like", "dislike"):
            return JsonResponse({"error": "Geçersiz feedback türü."}, status=400)

        user = request.user if request.user.is_authenticated else None
        logger.info(f"User: {user}")

        # ChatLog'u bul - feedback_id actually corresponds to chatlog.id
        try:
            chatlog = ChatLog.objects.get(id=feedback_id)  # Changed from chatlog_id to feedback_id
            logger.info(f"ChatLog bulundu: {chatlog}")
        except ChatLog.DoesNotExist:
            logger.error(f"ChatLog bulunamadı: {feedback_id}")
            return JsonResponse({"error": "ChatLog not found"}, status=404)

        # Feedback oluştur veya güncelle
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
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({"error": "Geçersiz JSON formatı"}, status=400)
    
    except ChatLog.DoesNotExist:
        logger.error(f"ChatLog not found: {feedback_id}")
        return JsonResponse({"error": "ChatLog not found"}, status=404)
    
    except Exception as e:
        logger.error(f"Feedback endpoint error: {str(e)}")
        return JsonResponse({"error": f"Bir hata oluştu: {str(e)}"}, status=500)