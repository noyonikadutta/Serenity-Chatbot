from collections import deque
import heapq
import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(__file__), 'memory.json')

# ---------------------------------------------------------
# 1. HASH TABLE (Dictionary) - Persistent User Profile
# ---------------------------------------------------------
class UserProfile:
    """
    Manages persistent user data using a Hash Table (Python Dictionary).
    Stores key attributes like name, age, and preferences.
    """
    def __init__(self):
        self.profile = {
            "name": None,
            "age": None,
            "preferences": [],
            "important_facts": {}
        }

    def update(self, key, value):
        """Updates a specific field in the user profile."""
        if value is not None:
            if key == "preferences" and isinstance(value, list):
                # append new preferences ensuring uniqueness
                current_prefs = set(self.profile["preferences"])
                for v in value:
                    current_prefs.add(v)
                self.profile["preferences"] = list(current_prefs)
            elif key == "preferences" and isinstance(value, str):
                 if value not in self.profile["preferences"]:
                    self.profile["preferences"].append(value)
            else:
                self.profile[key] = value
            print(f"[MEMORY] Updated Profile -> {key}: {value}")

    def get(self, key):
        """Retrieves a value from the user profile."""
        return self.profile.get(key)

    def to_string(self):
        """Returns a formatted string of the user profile for context."""
        return json.dumps(self.profile, indent=2)

    def to_dict(self):
        return self.profile

    def from_dict(self, data):
        if data:
            self.profile = data

# ---------------------------------------------------------
# 2. GRAPH - Emotion Transition Graph
# ---------------------------------------------------------
class EmotionGraph:
    """
    Tracks emotional state transitions using a directed weighted graph.
    Nodes are emotions. Edges represent transitions (Old Emotion -> New Emotion).
    Weights represent the frequency of this transition.
    """
    def __init__(self):
        self.adj_list = {} # { 'current_emotion': { 'next_emotion': count } }
        self.current_emotion = "neutral"

    def add_transition(self, new_emotion):
        """Updates the graph with a transition from current_emotion to new_emotion."""
        if not new_emotion:
            return

        normalized_emotion = new_emotion.lower()
        
        # Initialize node if not present
        if self.current_emotion not in self.adj_list:
            self.adj_list[self.current_emotion] = {}
        
        # Update edge weight
        if normalized_emotion in self.adj_list[self.current_emotion]:
            self.adj_list[self.current_emotion][normalized_emotion] += 1
        else:
            self.adj_list[self.current_emotion][normalized_emotion] = 1
            
        print(f"[MEMORY] Emotion Transition: {self.current_emotion} -> {normalized_emotion}")
        self.current_emotion = normalized_emotion

    def get_dominant_state(self):
        """Returns the current emotional state."""
        return self.current_emotion

    def to_dict(self):
        return {
            "adj_list": self.adj_list,
            "current_emotion": self.current_emotion
        }

    def from_dict(self, data):
        if data:
            self.adj_list = data.get("adj_list", {})
            self.current_emotion = data.get("current_emotion", "neutral")

# ---------------------------------------------------------
# 3. STACK - Recent Conversation Context
# ---------------------------------------------------------
class ContextStack:
    """
    LIFO Stack to store the last N conversation turns for immediate context.
    """
    def __init__(self, limit=5):
        self.stack = []
        self.limit = limit

    def push(self, turn):
        """Pushes a new conversation turn onto the stack."""
        self.stack.append(turn)
        if len(self.stack) > self.limit:
            self.stack.pop(0) # Maintain size limit (removing oldest from bottom to keep stack behavior for retrieval)
            # Note: strictly for a stack we pop from top, but for context window we keep recent N. 
            # Implemented as list where append is push, and we treat end as top.
        
    def peek(self):
        """Returns the most recent turn without removing it."""
        return self.stack[-1] if self.stack else None

    def get_recent_history(self):
        """Returns the list of recent turns."""
        return self.stack

    def to_dict(self):
        return {"stack": self.stack}

    def from_dict(self, data):
        if data:
            self.stack = data.get("stack", [])

# ---------------------------------------------------------
# 4. QUEUE - Chronological Message Log
# ---------------------------------------------------------
class MessageLog:
    """
    FIFO Queue to store the full chronological log of messages.
    """
    def __init__(self):
        self.queue = deque()

    def enqueue(self, message):
        """Adds a message to the end of the queue."""
        self.queue.append(message)

    def get_all_logs(self):
        """Returns all logs as a list."""
        return list(self.queue)

    def to_dict(self):
        return {"queue": list(self.queue)}

    def from_dict(self, data):
        if data:
            self.queue = deque(data.get("queue", []))

# ---------------------------------------------------------
# 5. TREE - Therapy Topic Hierarchy
# ---------------------------------------------------------
class TopicNode:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)
    
    def to_dict(self):
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children]
        }
    
    @staticmethod
    def from_dict(data):
        node = TopicNode(data["name"])
        for child_data in data.get("children", []):
            node.add_child(TopicNode.from_dict(child_data))
        return node

class TopicTree:
    """
    Tree structure to organize therapy topics hierarchically.
    Root -> Categories -> Specific Topics
    """
    def __init__(self):
        self.root = TopicNode("Therapy Session")
        # Pre-seed some common categories
        self.categories = {
            "work": TopicNode("Work"),
            "relationships": TopicNode("Relationships"),
            "health": TopicNode("Health"),
            "self": TopicNode("Self-Improvement")
        }
        for node in self.categories.values():
            self.root.add_child(node)

    def add_topic(self, topic):
        """Adds a discovered topic to the tree under a generic 'Discovered' category or maps it."""
        # Simple implementation: Add to a 'General' node if not mapped
        # In a real app this would be more complex
        if not topic:
            return
            
        found = False
        # Very basic keyword matching to place in tree
        topic_lower = topic.lower()
        if "boss" in topic_lower or "job" in topic_lower:
             self.categories["work"].add_child(TopicNode(topic))
             found = True
        elif "partner" in topic_lower or "friend" in topic_lower:
             self.categories["relationships"].add_child(TopicNode(topic))
             found = True
        
        if not found:
             # Just add to root for now if no category match
             self.root.add_child(TopicNode(topic))
        
        print(f"[MEMORY] Logged Topic: {topic}")

    def to_dict(self):
        return {"root": self.root.to_dict()}

    def from_dict(self, data):
        # Note: We are overwriting the default structure if loading from disk
        # Ideally, we should merge, but for this task, loading the state is sufficient.
        if data and "root" in data:
            self.root = TopicNode.from_dict(data["root"])
            # Re-link categories for easy access if they exist in the loaded tree
            # This is a simplification; in a real app, we'd traverse to find them.
            # Here we assume the structure is preserved.
            for child in self.root.children:
                key = child.name.lower()
                if key == "self-improvement": key = "self" # mapping back
                if key in self.categories:
                    self.categories[key] = child

# ---------------------------------------------------------
# 6. SET - Unique Entities
# ---------------------------------------------------------
class EntitySet:
    """
    Set to store unique user-mentioned entities (people, places, specific nouns).
    Ensures no duplicates.
    """
    def __init__(self):
        self.entities = set()

    def add(self, entity):
        """Adds a new entity to the set."""
        if entity:
            self.entities.add(entity)
            print(f"[MEMORY] Tracked Entity: {entity}")

    def get_all(self):
        return list(self.entities)

    def to_dict(self):
        return {"entities": list(self.entities)}

    def from_dict(self, data):
        if data:
            self.entities = set(data.get("entities", []))

# ---------------------------------------------------------
# 7. PRIORITY QUEUE - Emotional Urgency
# ---------------------------------------------------------
class UrgencyQueue:
    """
    Priority Queue to manage messages based on emotional urgency.
    Higher urgency score messages are dequeued first (simulated processing priority).
    """
    def __init__(self):
        self.heap = []
        self.index = 0 # Tie-breaker

    def add(self, message, emotion):
        """
        Calculates urgency score based on emotion and pushes to heap.
        Heaps are min-heaps in Python, so we use negative score for max-priority behavior.
        """
        score = 0
        if emotion in ["stressed", "anxious", "angry", "crisis"]:
            score = 10
        elif emotion in ["sad", "depressed"]:
            score = 8
        elif emotion in ["happy", "neutral"]:
            score = 1
        
        # Push tuple (-score, index, message)
        heapq.heappush(self.heap, (-score, self.index, message))
        self.index += 1
        print(f"[MEMORY] Urgency Score {score} for emotion '{emotion}'")

    def get_highest_priority(self):
        """Returns the highest urgency message."""
        if self.heap:
            return heapq.heappop(self.heap)[2]
        return None

    def to_dict(self):
        return {"heap": self.heap, "index": self.index}

    def from_dict(self, data):
        if data:
            raw_heap = data.get("heap", [])
            # JSON deserializes tuples as lists, so we must convert them back
            # ensuring consistent types in the heap.
            self.heap = [tuple(item) for item in raw_heap]
            self.index = data.get("index", 0)
            heapq.heapify(self.heap) # Ensure heap property is maintained

# ---------------------------------------------------------
# GLOBAL MEMORY STORE
# ---------------------------------------------------------
class GlobalMemory:
    def __init__(self):
        self.user_profile = UserProfile()
        self.emotion_graph = EmotionGraph()
        self.context_stack = ContextStack()
        self.message_log = MessageLog()
        self.topic_tree = TopicTree()
        self.entity_set = EntitySet()
        self.urgency_queue = UrgencyQueue()
        
        # Load from disk on startup
        self.load_from_disk()

    def save_to_disk(self):
        """Serializes all memory structures and saves to JSON file."""
        data = {
            "user_profile": self.user_profile.to_dict(),
            "emotion_graph": self.emotion_graph.to_dict(),
            "context_stack": self.context_stack.to_dict(),
            "message_log": self.message_log.to_dict(),
            "topic_tree": self.topic_tree.to_dict(),
            "entity_set": self.entity_set.to_dict(),
            "urgency_queue": self.urgency_queue.to_dict()
        }
        try:
            with open(MEMORY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print("[MEMORY] State saved to memory.json")
        except Exception as e:
            print(f"[MEMORY] Error saving state: {e}")

    def load_from_disk(self):
        """Loads memory state from JSON file if it exists."""
        if not os.path.exists(MEMORY_FILE):
            print("[MEMORY] No persistence file found. Starting fresh.")
            return

        try:
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
            
            self.user_profile.from_dict(data.get("user_profile"))
            self.emotion_graph.from_dict(data.get("emotion_graph"))
            self.context_stack.from_dict(data.get("context_stack"))
            self.message_log.from_dict(data.get("message_log"))
            self.topic_tree.from_dict(data.get("topic_tree"))
            self.entity_set.from_dict(data.get("entity_set"))
            self.urgency_queue.from_dict(data.get("urgency_queue"))
            
            print("[MEMORY] Loaded state from memory.json")
        except Exception as e:
            print(f"[MEMORY] Error loading persistence file: {e}")

    def clear(self):
        """Resets all memory structures to initial state."""
        self.user_profile = UserProfile()
        self.emotion_graph = EmotionGraph()
        self.context_stack = ContextStack()
        self.message_log = MessageLog()
        self.topic_tree = TopicTree()
        self.entity_set = EntitySet()
        self.urgency_queue = UrgencyQueue()
        self.save_to_disk()
        print("[MEMORY] Memory cleared.")

# Instantiate single global memory object
memory = GlobalMemory()
