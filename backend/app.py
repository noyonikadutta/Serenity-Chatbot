from flask import Flask, request, jsonify
from flask_cors import CORS
from logic import process_chat
from rag import rag_bot
from crs_evaluator import crs_evaluator

app = Flask(__name__)
CORS(app) # Enable CORS for all roots to allow frontend integration

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint for the Memory-Centric Bot.
    """
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"reply": "I'm here. You can say anything."})

        # Process via Memory Logic
        reply, memory_snapshot = process_chat(user_message)
        
        # Calculate CRS for memory-based system
        crs_metrics = crs_evaluator.calculate_crs_for_memory(reply, memory_snapshot)
        
        return jsonify({
            "reply": reply,
            "debug_data": memory_snapshot,
            "crs_metrics": crs_metrics
        })

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"reply": "I apologize, I'm having a little trouble connecting right now.", "error": str(e)}), 500

@app.route('/chat/rag', methods=['POST'])
def chat_rag():
    """
    Endpoint for the RAG Baseline Bot.
    """
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"reply": "Please go on."})
            
        # Process via RAG Logic
        reply = rag_bot.process_chat(user_message)
        
        # Calculate CRS for RAG-based system (checking immediate context)
        crs_metrics = crs_evaluator.calculate_crs_for_rag(reply, user_message)
        
        return jsonify({
            "reply": reply,
            "crs_metrics": crs_metrics
        })
    except Exception as e:
        print(f"RAG Error: {e}")
        return jsonify({"reply": "I am unable to access my references."}), 500

@app.route('/crs/metrics', methods=['GET'])
def get_crs_metrics():
    """
    Endpoint for CRS Comparison Dashboard.
    Returns Context Retention Scores for both systems.
    """
    try:
        avg_scores = crs_evaluator.get_average_scores()
        return jsonify(avg_scores)
    except Exception as e:
        print(f"CRS Metrics Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/session/reset', methods=['POST'])
def reset_session():
    """
    Endpoint to clear Memory Bot's state and start fresh.
    """
    try:
        from memory import memory
        memory.clear()
        
        # Reset CRS evaluator as well
        crs_evaluator.reset() 
        
        return jsonify({"status": "success", "message": "Memory and metrics reset."})
    except Exception as e:
        print(f"Reset Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Serenity Backend on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
