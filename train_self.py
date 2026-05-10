import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from logic import Game, encode_board

class ValueNet(nn.Module):
    def __init__(self, input_size=64, hidden_size=64):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)
        self.tanh = nn.Tanh()
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return self.tanh(x)

def choose_move(state, model, epsilon=0.1):
    moves = state.possible_moves()
    if not moves:
        return None
    if random.random() < epsilon:
        return random.choice(moves)
    best_move = None
    best_value = -float('inf')
    for move in moves:
        next_state = state.do_move(move)
        features = torch.tensor(encode_board(next_state.board), dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            value = -model(features).item()
        if value > best_value:
            best_value = value
            best_move = move
    return best_move

def play_episode(model, epsilon=0.1):
    state = Game()
    trajectory = []  
    while not state.is_game_over():
        features_before = encode_board(state.board)
        move = choose_move(state, model, epsilon)
        if move is None:
            break
        state = state.do_move(move)
        trajectory.append((features_before, move))
    result = state.result()  
    final_reward = -result
    discounted = 0.9
    rewards = []
    for i in range(len(trajectory)-1, -1, -1):
        discounted *= 0.9
        rewards.append(discounted * final_reward)
    rewards.reverse()
    return [(traj[0], rewards[i]) for i, traj in enumerate(trajectory)]

model = ValueNet()
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

num_episodes = 500
batch_size = 32

for episode in range(num_episodes):
    experience = []
    for _ in range(batch_size):
        exp = play_episode(model, epsilon=0.1)
        experience.extend(exp)
    for features, target_value in experience:
        features_t = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        pred = model(features_t)
        loss = criterion(pred, torch.tensor([[target_value]], dtype=torch.float32))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

torch.save(model.state_dict(), 'value_net.pth')
print("Модель сохранена")
