# Serenity Chatbot Backend

This is the Python Flask backend for the Serenity Therapy Chatbot. It uses manual memory management with classical data structures (DSA) and integrates with **Grok AI** (xAI) for semantic understanding.

## Setup Instructions

1. **Install Python**: Ensure you have Python 3.11+ installed.

2. **Navigate to Backend**:
   ```bash
   cd backend
   ```

3. **Configure API Key**:
   
   Get your Grok API key from [console.x.ai](https://console.x.ai)
   
   Then edit the `.env.local` file in the project root:
   ```env
   GROK_API_KEY=your-actual-grok-api-key-here
   ```
   
   Replace `your-actual-grok-api-key-here` with your real Grok API key.

4. **Run the Server**:
   ```bash
   python app.py
   ```
   The server will start on `http://127.0.0.1:5000`.
   
   You should see:
   ```
   [CONFIG] API Key loaded: ✓ Configured
   Starting Serenity Backend on http://127.0.0.1:5000
   ```

## API Configuration

- **Provider**: Grok AI (xAI)
- **Base URL**: `https://api.x.ai/v1`
- **Model**: `grok-beta`
- **API Key Location**: `.env.local` file (variable: `GROK_API_KEY`)

## Memory Logic (DSA)

- **Hash Table**: Stores persistent user attributes (Name, etc.).
- **Graph**: Tracks emotional transitions.
- **Stack**: Maintains recent conversation turns (last 5).
- **Queue**: Logs every message chronologically.
- **Tree**: Hierarchical topic organization.
- **Set**: Tracks unique entities mentioned.
- **Priority Queue**: Scores messages by emotional urgency.

The bot uses **Context Injection**. Before every reply, it retrieves data from all these structures, builds a "Memory Context" string, and feeds it to Gemini. This ensures the bot never "forgets" your name or feelings even if the internal LLM context window is reset.
