"""
Classifier module for the Shadow Orchestrator.

This module contains the logic for classifying user inputs and determining
which specialized agent(s) should handle a request.
"""

from typing import List


class InputClassifier:
    """
    Classifies user input to determine which agent(s) should process the request.
    
    The classifier uses keyword matching and other heuristics to route
    requests appropriately to Engineer, Librarian, and/or Priest agents.
    """
    
    def __init__(self):
        # Define keywords for each agent domain
        self.engineer_keywords = [
            "build", "design", "calculate", "model", "simulate", 
            "create", "develop", "construct", "code", "program", 
            "engineer", "architecture", "system", "technical",
            "process", "optimize", "efficiency", "algorithm"
        ]
        
        self.librarian_keywords = [
            "reference", "search", "find", "lookup", "cite",
            "information", "data", "source", "document", "record",
            "retrieve", "index", "catalog", "organize", "categorize",
            "research", "history", "facts", "details"
        ]
        
        self.priest_keywords = [
            "ethics", "moral", "philosophy", "should we", "is it right",
            "belief", "religion", "spiritual", "value", "principle",
            "good", "evil", "virtue", "vice", "duty", "obligation",
            "meaning", "purpose", "life", "death", "existence"
        ]
    
    def classify_task(self, user_input: str) -> List[str]:
        """
        Classify user input to determine appropriate agent(s).
        
        Args:
            user_input: The user's request text
            
        Returns:
            A list of agent names that should process the request
        """
        user_input = user_input.lower()
        agents = []
        
        # Check for engineer keywords
        if any(keyword in user_input for keyword in self.engineer_keywords):
            agents.append("engineer")
            
        # Check for librarian keywords
        if any(keyword in user_input for keyword in self.librarian_keywords):
            agents.append("librarian")
            
        # Check for priest keywords
        if any(keyword in user_input for keyword in self.priest_keywords):
            agents.append("priest")
        
        # Default to librarian if no specific agent is identified
        if not agents:
            agents.append("librarian")
        
        return agents
    
    def classify_with_confidence(self, user_input: str) -> dict:
        """
        Classify with confidence scores for each agent type.
        
        Args:
            user_input: The user's request text
            
        Returns:
            Dictionary with agent names and confidence scores
        """
        user_input = user_input.lower()
        confidence = {"engineer": 0.0, "librarian": 0.0, "priest": 0.0}
        
        # Count keyword matches for each agent type
        for keyword in self.engineer_keywords:
            if keyword in user_input:
                confidence["engineer"] += 1.0
                
        for keyword in self.librarian_keywords:
            if keyword in user_input:
                confidence["librarian"] += 1.0
                
        for keyword in self.priest_keywords:
            if keyword in user_input:
                confidence["priest"] += 1.0
        
        # Normalize confidence scores
        total = sum(confidence.values())
        if total > 0:
            for agent in confidence:
                confidence[agent] /= total
        else:
            # Default to librarian with low confidence
            confidence["librarian"] = 0.5
        
        return confidence


# Create a default instance for easy import
default_classifier = InputClassifier()


def classify_input(user_input: str) -> List[str]:
    """
    Simple wrapper function to classify user input using the default classifier.
    
    Args:
        user_input: The user's request text
        
    Returns:
        List of agent names that should process the request
    """
    return default_classifier.classify_task(user_input)
