from memory import memory
from llm import extract_metadata, generate_response
import datetime

def process_chat(user_message):
    """
    Main logic pipeline:
    1. Extract Metadata (LLM)
    2. Update Memory (DSA)
    3. Retrieve Context (DSA)
    4. Generate Response (LLM)
    """
    print(f"\n--- Processing Message: '{user_message}' ---")

    # -----------------------------------------------------
    # 1. EXTRACT DATA
    # -----------------------------------------------------
    # Call Gemini to get structured JSON analysis
    metadata = extract_metadata(user_message)
    
    # -----------------------------------------------------
    # 2. UPDATE MEMORY
    # -----------------------------------------------------
    
    # A. Update User Profile (Hash Table)
    facts = metadata.get("facts", {})
    if facts.get("name"):
        memory.user_profile.update("name", facts["name"])
    if facts.get("age"):
        memory.user_profile.update("age", facts["age"])
    if facts.get("preferences"):
        memory.user_profile.update("preferences", facts["preferences"])

    # B. Update Emotion Graph
    emotion = metadata.get("emotion", "neutral")
    memory.emotion_graph.add_transition(emotion)
    
    # C. Update Topic Tree (Tree)
    topics = metadata.get("topics", [])
    for topic in topics:
        memory.topic_tree.add_topic(topic)
        
    # D. Update Entity Set (Set)
    entity = metadata.get("entity")
    if entity:
        memory.entity_set.add(entity)
        
    # E. Update Urgency Queue (Priority Queue)
    memory.urgency_queue.add(user_message, emotion)
    
    # F. Update Message Log (Queue)
    # Storing structured log
    log_entry = {
        "timestamp": str(datetime.datetime.now()), # fixed time call
        "role": "user",
        "content": user_message,
        "emotion": emotion
    }
    memory.message_log.enqueue(log_entry)
    
    # G. Update Context Stack (Stack)
    # Pushing raw text for immediate recall
    memory.context_stack.push(f"User: {user_message}")

    # -----------------------------------------------------
    # PERSISTENCE CHECKPOINT
    # -----------------------------------------------------
    memory.save_to_disk()

    # -----------------------------------------------------
    # 3. BUILD CONTEXT
    # -----------------------------------------------------
    
    # Retrieve data from all structures to feed the LLM
    profile_str = memory.user_profile.to_string()
    current_emotion = memory.emotion_graph.get_dominant_state()
    recent_history = memory.context_stack.get_recent_history()
    entities = memory.entity_set.get_all()
    
    context_str = f"""
    USER PROFILE: {profile_str}
    CURRENT EMOTION STATE: {current_emotion}
    RECENT CONVERSATION: {recent_history}
    KNOWN ENTITIES: {entities}
    """
    
    print("--- Built Context for LLM ---")
    print(context_str.strip())
    print("-----------------------------")

    # -----------------------------------------------------
    # 4. GENERATE RESPONSE
    # -----------------------------------------------------
    reply = generate_response(user_message, context_str)
    
    # Log assistant reply to stack as well
    memory.context_stack.push(f"Serenity: {reply}")
    
    # Prepare memory snapshot for frontend visualization
    memory_snapshot = {
        "user_profile": memory.user_profile.to_dict(),
        "emotion_graph": memory.emotion_graph.to_dict(),
        "topics": memory.topic_tree.to_dict(),
        "urgency": memory.urgency_queue.to_dict()
    }
    
    return reply, memory_snapshot
