import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from ticketing.models import Bus, Route, Ticket

class GeminiBusChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_message = request.data.get("message", "").strip()

        if not user_message:
            return Response({"error": "Message is required"}, status=400)

        # ----------------------
        # Prepare DB context
        # ----------------------
        db_context = ""

        if "bus" in user_message.lower() or "route" in user_message.lower():
            routes = Route.objects.all()[:5]
            buses = Bus.objects.all()[:5]
            db_context += "Available routes:\n"
            for r in routes:
                db_context += f"- {r.start_point} → {r.end_point}, {r.distance_km} km\n"
            db_context += "Available buses:\n"
            for b in buses:
                db_context += f"- Bus {b.bus_number}, capacity {b.capacity}\n"

        if "my ticket" in user_message.lower():
            tickets = Ticket.objects.filter(user=user).select_related("bus", "route")[:5]
            db_context += "Your tickets:\n"
            for t in tickets:
                db_context += f"- Ticket {t.id}, bus {t.bus.bus_number}, route {t.route}, seat {t.seat_number}, status {t.status}\n"

        # ----------------------
        # Call Gemini API
        # ----------------------
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GEMINI_API_KEY
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"User asked: {user_message}\nDatabase facts:\n{db_context}"}
                    ]
                }
            ]
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
        except requests.Timeout:
            return Response({"error": "Gemini API timed out"}, status=504)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        if resp.status_code != 200:
            return Response({"error": "Gemini API error", "details": resp.text}, status=502)

        data = resp.json()
        try:
            response_text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            response_text = "Sorry, I couldn't understand the response."

        return Response({
            "user_message": user_message,
            "db_context": db_context,
            "response": response_text
        })
