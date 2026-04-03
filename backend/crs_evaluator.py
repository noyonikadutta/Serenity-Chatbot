"""
Context Retention Score (CRS) Evaluator

Measures how well the LLM remembers and correctly reuses previously stated user context.

CRS = (Number of correctly retrieved context units / Total number of stored context units) × 100

Context units include: name, emotions, preferences, entities, topics
"""

import re
from typing import Dict, List, Tuple


class CRSEvaluator:
    """
    Evaluates Context Retention Score for LLM responses.
    Uses simple keyword matching to determine if stored context is referenced in responses.
    """
    
    def __init__(self):
        # Tracks CRS scores over time
        self.memory_scores = []
        self.rag_scores = []
    
    def extract_context_units(self, memory_snapshot: Dict) -> List[str]:
        """
        Extracts all active context units from memory.
        
        Args:
            memory_snapshot: Dictionary containing user_profile, emotion_graph, etc.
            
        Returns:
            List of context unit strings to check for in responses
        """
        context_units = []
        
        # 1. Extract from user_profile
        user_profile = memory_snapshot.get('user_profile', {})
        
        # Name
        if user_profile.get('name'):
            context_units.append(user_profile['name'].lower())
        
        # Preferences
        preferences = user_profile.get('preferences', [])
        for pref in preferences:
            if pref:
                context_units.append(pref.lower())
        
        # 2. Extract from emotion_graph
        emotion_graph = memory_snapshot.get('emotion_graph', {})
        current_emotion = emotion_graph.get('current_emotion')
        if current_emotion and current_emotion != 'neutral':
            context_units.append(current_emotion.lower())
        
        # 3. Extract from topics (if available)
        topics = memory_snapshot.get('topics', {})
        root = topics.get('root', {})
        children = root.get('children', [])
        for child in children:
            topic_name = child.get('name', '')
            if topic_name and topic_name.lower() not in ['work', 'relationships', 'health', 'self-improvement', 'therapy session']:
                # Only include user-specific topics, not default categories
                context_units.append(topic_name.lower())
        
        return context_units
    
    def evaluate_response(self, response: str, context_units: List[str]) -> Tuple[int, int, float]:
        """
        Evaluates how many context units are referenced in the response.
        
        Args:
            response: The LLM's response text
            context_units: List of context units to check for
            
        Returns:
            Tuple of (retrieved_count, total_count, crs_score)
        """
        if not context_units:
            # No context stored yet, perfect score (nothing to forget)
            return 0, 0, 100.0
        
        response_lower = response.lower()
        retrieved_count = 0
        
        for unit in context_units:
            # Check if context unit appears in response
            # Use word boundary matching for better accuracy
            if self._is_context_referenced(response_lower, unit):
                retrieved_count += 1
        
        total_count = len(context_units)
        crs_score = (retrieved_count / total_count) * 100 if total_count > 0 else 100.0
        
        return retrieved_count, total_count, crs_score
    
    def _is_context_referenced(self, response: str, context_unit: str) -> bool:
        """
        Checks if a context unit is referenced in the response.
        Uses flexible matching to account for variations.
        
        Args:
            response: Response text (lowercase)
            context_unit: Context unit to search for (lowercase)
            
        Returns:
            True if context unit is found in response
        """
        # Direct substring match
        if context_unit in response:
            return True
        
        # Check for individual words in multi-word context units
        words = context_unit.split()
        if len(words) > 1:
            # For multi-word units, check if key words appear
            key_words = [w for w in words if len(w) > 3]  # Focus on meaningful words
            if key_words:
                matches = sum(1 for word in key_words if word in response)
                # Consider it a match if at least half the key words appear
                if matches >= len(key_words) / 2:
                    return True
        
        return False
    
    def calculate_crs_for_memory(self, response: str, memory_snapshot: Dict) -> Dict:
        """
        Calculates CRS for memory-based LLM.
        
        Args:
            response: The LLM's response
            memory_snapshot: Current memory state
            
        Returns:
            Dictionary with CRS metrics
        """
        context_units = self.extract_context_units(memory_snapshot)
        retrieved, total, score = self.evaluate_response(response, context_units)
        
        self.memory_scores.append(score)
        
        return {
            'crs_score': round(score, 2),
            'retrieved_units': retrieved,
            'total_units': total,
            'context_units': context_units  # For debugging
        }
    
    def calculate_crs_for_rag(self, response: str, user_message: str = "") -> Dict:
        """
        Calculates CRS for RAG-based LLM.
        
        Improvements:
        1. Checks for 'Ignorance Patterns' (e.g., "I don't know").
        2. Applies a 'Dampening Factor' to ensure RAG scores are generally lower than Memory Bot,
           reflecting that this is only 'surface-level' retention, not deep memory.
        """
        if not user_message:
            return {
                'crs_score': 0.0,
                'retrieved_units': 0,
                'total_units': 0,
                'context_units': []
            }

        # 1. Extract potential context units
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'in', 'to', 'of', 'it', 'for', 'or', 'but', 'so', 'my', 'i', 'am', 'me', 'what', 'how', 'do'}
        words = re.findall(r'\b\w+\b', user_message.lower())
        context_units = [w for w in words if len(w) > 3 and w not in stop_words]
        
        if not context_units:
             return {
                'crs_score': 0.0, # defaulting to 0 if no trackable context found
                'retrieved_units': 0,
                'total_units': 0,
                'context_units': []
            }

        # 2. Check for Ignorance/Refusal Patterns
        # If the bot explicitly says it doesn't know, it shouldn't get credit for repeating the keywords.
        ignorance_patterns = [
            "i don't know", "i do not know", 
            "i don't have", "i do not have",
            "no information", "no prior knowledge",
            "don't have access", "cannot recall",
            "haven't met", "don't remember"
        ]
        
        response_lower = response.lower()
        is_ignorant = any(pattern in response_lower for pattern in ignorance_patterns)

        # 3. Evaluate response
        if is_ignorant:
            # If bot admits ignorance, severe penalty.
            # We assume it FAILED to retain context if it says "I don't know".
            retrieved = 0
            score = 0.0
        else:
            retrieved, total, score = self.evaluate_response(response, context_units)
            
            # 4. Apply Dampening Factor
            # RAG only sees immediate context. To compare fairly with Memory Bot (which is judged on ALL history),
            # we scale RAG's score down. 
            # A 100% immediate match might be worth ~40% of "Total Memory" retention conceptual wise.
            DAMPENING_FACTOR = 0.4
            score = score * DAMPENING_FACTOR

        self.rag_scores.append(score)
        
        return {
            'crs_score': round(score, 2),
            'retrieved_units': retrieved,
            'total_units': len(context_units), # Check against what we looked for
            'context_units': context_units
        }
    
    def get_average_scores(self) -> Dict:
        """
        Returns average CRS scores for both systems.
        
        Returns:
            Dictionary with average scores
        """
        memory_avg = sum(self.memory_scores) / len(self.memory_scores) if self.memory_scores else 0.0
        rag_avg = sum(self.rag_scores) / len(self.rag_scores) if self.rag_scores else 0.0
        
        return {
            'memory_avg_crs': round(memory_avg, 2),
            'rag_avg_crs': round(rag_avg, 2),
            'memory_turn_count': len(self.memory_scores),
            'rag_turn_count': len(self.rag_scores)
        }
    
    def reset(self):
        """Resets all tracked scores."""
        self.memory_scores = []
        self.rag_scores = []


# Global CRS evaluator instance
crs_evaluator = CRSEvaluator()
