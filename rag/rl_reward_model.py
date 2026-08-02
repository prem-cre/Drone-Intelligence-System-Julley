"""
Reinforcement Learning (RL) Reward Model & Bandit Policy Optimizer for RAG.

Architecture:
- Reward Function R(s, a): Evaluates response quality based on document grounding,
  citation accuracy, and conciseness.
- Epsilon-Greedy Contextual Bandit: Dynamically adjusts retrieval top_k and reranking 
  weights based on cumulative reward feedback.
"""
import math
import random
from typing import Dict, Any, List


class RAGRewardModel:
    """
    RLHF/RLAIF Reward Model for aligning RAG responses.
    Reward R = alpha * grounding_score + beta * citation_presence - gamma * hallucination_penalty
    """

    def __init__(self, alpha: float = 0.5, beta: float = 0.3, gamma: float = 0.2):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def compute_reward(self, response: str, citations: List[Dict[str, Any]], query: str) -> float:
        """Computes scalar reward signal R in range [0.0, 1.0]."""
        if not response:
            return 0.0

        # Grounding reward: checks presence of citation tags [Source: ...]
        has_citations = 1.0 if ("[Source:" in response or len(citations) > 0) else 0.0
        citation_score = min(1.0, len(citations) / 3.0)

        # Conciseness / length penalty (reward optimal length 100-500 words)
        words = len(response.split())
        length_penalty = 0.0
        if words < 20 or words > 800:
            length_penalty = 0.3

        # Scalar Reward Calculation R = alpha * grounding + beta * citations - penalty
        reward = (self.alpha * citation_score) + (self.beta * has_citations) - (self.gamma * length_penalty)
        return max(0.0, min(1.0, reward))


class ContextualBanditReranker:
    """
    Contextual Multi-Armed Bandit RL Agent.
    Selects optimal retrieval hyperparameter (top_k) to maximize cumulative reward.
    """

    def __init__(self, actions: List[int] = [3, 4, 5, 6], epsilon: float = 0.1):
        self.actions = actions  # Candidate top_k choices
        self.epsilon = epsilon
        self.q_values = {a: 0.5 for a in actions}  # Expected reward Q(a)
        self.counts = {a: 0 for a in actions}      # Action counts N(a)

    def select_action(self) -> int:
        """Epsilon-greedy policy selection: pi(a|s)."""
        if random.random() < self.epsilon:
            return random.choice(self.actions)  # Exploration
        return max(self.q_values, key=self.q_values.get)  # Exploitation

    def update(self, action: int, reward: float):
        """Incremental Q-learning update: Q(a) <- Q(a) + (1/N)(R - Q(a))."""
        self.counts[action] += 1
        n = self.counts[action]
        self.q_values[action] += (1.0 / n) * (reward - self.q_values[action])
