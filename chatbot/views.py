from django.shortcuts import render

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def chatbot_reply(request):
    # ✅ READ MESSAGE FROM QUERY PARAM
    message = request.GET.get("message", "").lower().strip()

    if not message:
        return JsonResponse({"reply": "❌ Please type something"})

    # ------------------
    # SMART BOT LOGIC
    # ------------------
    if message in ["hi", "hello", "hey"]:
        reply = "👋 Hi! How can I help you today?"

    elif "job" in message:
        reply = "📝 You can browse jobs or post a new job from your dashboard."

    elif "proposal" in message:
        reply = "📄 Proposals help freelancers apply for jobs. Recruiters can accept or reject them."

    elif "chat" in message:
        reply = "💬 You can chat after a proposal is accepted."

    elif "resume" in message:
        reply = "📎 You can upload your resume while applying for a job."

    elif "bye" in message:
        reply = "👋 Goodbye! Have a great day 😊"

    else:
        reply = "🤖 I didn’t understand that. Try asking about jobs, proposals, chat, or resume."

    return JsonResponse({"reply": reply})
