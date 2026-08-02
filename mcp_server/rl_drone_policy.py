"""
Reinforcement Learning (RL) Q-Learning Agent for Drone Hover & Battery Optimization.

Markov Decision Process (MDP):
- State Space S: (battery_pct, wind_speed_level, payload_level)
- Action Space A: {0: Low Power Hover, 1: Optimal Thrust, 2: Maximum Stabilization}
- Reward R: R = altitude_hold_stability - (battery_draw_rate * wind_penalty)
- Bellman Equation: Q(s,a) <- Q(s,a) + alpha * [r + gamma * max_a' Q(s',a') - Q(s,a)]
"""
import random
from typing import Tuple, Dict


class QLearningDronePolicy:
    """
    Q-Learning RL Agent for optimizing drone flight stability and battery usage.
    """

    def __init__(self, alpha: float = 0.1, gamma: float = 0.95, epsilon: float = 0.1):
        self.alpha = alpha     # Learning rate
        self.gamma = gamma     # Discount factor
        self.epsilon = epsilon # Exploration rate
        self.q_table: Dict[Tuple[int, int, int], Dict[int, float]] = {}

    def _get_q(self, state: Tuple[int, int, int], action: int) -> float:
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in [0, 1, 2]}
        return self.q_table[state][action]

    def select_action(self, state: Tuple[int, int, int]) -> int:
        """Epsilon-greedy policy pi(a|s)."""
        if random.random() < self.epsilon:
            return random.choice([0, 1, 2])
        
        if state not in self.q_table:
            return 1  # Default to Optimal Thrust
        return max(self.q_table[state], key=self.q_table[state].get)

    def learn(self, state: Tuple[int, int, int], action: int, reward: float, next_state: Tuple[int, int, int]):
        """Q-value update using Bellman Optimality Equation."""
        current_q = self._get_q(state, action)
        next_max_q = max(self._get_q(next_state, a) for a in [0, 1, 2])
        
        # Temporal Difference (TD) Error calculation
        td_target = reward + self.gamma * next_max_q
        self.q_table[state][action] += self.alpha * (td_target - current_q)
