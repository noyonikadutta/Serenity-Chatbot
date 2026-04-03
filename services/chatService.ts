
import { ChatResponse, Message } from '../types';

const API_BASE_URL = 'http://127.0.0.1:5000';

/**
 * Sends a message to the backend therapy chatbot endpoint.
 * Falls back to a simulated response if the backend is unavailable.
 */
export const sendMessageToBackend = async (
  message: string,
  history: Message[]
): Promise<ChatResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        // Optional: send history if backend supports context
        history: history.map(m => ({ role: m.role, content: m.content }))
      }),
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Backend connection failed:', error);
    // Simulate a thoughtful response if backend isn't running for demo purposes
    const reply = await simulateTherapistReply(message);
    return { reply };
  }
};

export const sendMessageToRag = async (message: string): Promise<{ reply: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/rag`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    if (!response.ok) throw new Error('RAG Endpoint failed');
    return await response.json();
  } catch (error) {
    console.error('RAG connection failed:', error);
    return { reply: "I am unable to access my reference materials right now (RAG Offline)." };
  }
};

export const resetSession = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/session/reset`, { method: 'POST' });
    return response.ok;
  } catch (error) {
    console.error("Reset failed:", error);
    return false;
  }
};

/**
 * Mocking a therapist response for when the local server is not running.
 * In a real production scenario, this would be handled by robust error states.
 */
const simulateTherapistReply = async (input: string): Promise<string> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const prompts = [
        "I hear what you're saying. Could you tell me more about how that makes you feel?",
        "It sounds like you've been carrying a lot lately. How are you taking care of yourself today?",
        "Thank you for sharing that with me. What do you think is at the heart of that concern?",
        "I'm here with you. Take your time. What else is on your mind?",
        "That sounds like a challenging situation. How have you navigated similar feelings in the past?"
      ];
      const randomReply = prompts[Math.floor(Math.random() * prompts.length)];
      resolve(randomReply);
    }, 1500);
  });
};
