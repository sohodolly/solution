import json
import math
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# ============ КОНФИГ ============
BASE = Path(r"C:\Users\supra\Music\prod\prog")
DATA_PATH = BASE / "dataset" / "encoded.json"
VOCAB_PATH = BASE / "dataset" / "vocab.json"
MODEL_PATH = BASE / "model.pt"

BLOCK_SIZE = 128      # контекст (длина последовательности)
BATCH_SIZE = 256       # размер батча
N_EMBD = 128          # размер эмбеддинга
N_HEAD = 4            # голов attention
N_LAYER = 4           # слоёв трансформера
DROPOUT = 0.1
LR = 3e-4
EPOCHS = 5
DEVICE = "cpu"
SEED = 1337

torch.manual_seed(SEED)

# ============ ДАННЫЕ ============
print("Загружаю датасет...")
with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)

with open(VOCAB_PATH, encoding="utf-8") as f:
    vocab = json.load(f)

VOCAB_SIZE = len(vocab)
print(f"Реплик: {len(data)}")
print(f"Словарь: {VOCAB_SIZE}")

# склеиваем всё в один длинный поток токенов, разделяя реплики
# (чтобы модель видела конец одной и начало следующей)
all_tokens = []
for seq in data:
    all_tokens.extend(seq)
all_tokens = torch.tensor(all_tokens, dtype=torch.long)
print(f"Всего токенов: {len(all_tokens)}")


class TokenDataset(Dataset):
    def __init__(self, tokens, block_size):
        self.tokens = tokens
        self.block_size = block_size

    def __len__(self):
        return len(self.tokens) - self.block_size - 1

    def __getitem__(self, idx):
        x = self.tokens[idx:idx + self.block_size]
        y = self.tokens[idx + 1:idx + self.block_size + 1]
        return x, y


# разбиваем на train/val (95/5)
n = len(all_tokens)
split = int(n * 0.95)
train_tokens = all_tokens[:split]
val_tokens = all_tokens[split:]

train_ds = TokenDataset(train_tokens, BLOCK_SIZE)
val_ds = TokenDataset(val_tokens, BLOCK_SIZE)

train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_dl = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

print(f"Train батчей: {len(train_dl)}, Val батчей: {len(val_dl)}")


# ============ МОДЕЛЬ ============
class Head(nn.Module):
    """Одна голова self-attention."""
    def __init__(self, n_embd, head_size, block_size, dropout):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)
        q = self.query(x)
        wei = q @ k.transpose(-2, -1) * (C ** -0.5)
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float("-inf"))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        v = self.value(x)
        return wei @ v


class MultiHeadAttention(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        head_size = n_embd // n_head
        self.heads = nn.ModuleList([
            Head(n_embd, head_size, block_size, dropout) for _ in range(n_head)
        ])
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout(self.proj(out))


class FeedForward(nn.Module):
    def __init__(self, n_embd, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        self.sa = MultiHeadAttention(n_embd, n_head, block_size, dropout)
        self.ffwd = FeedForward(n_embd, dropout)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x


class GPT(nn.Module):
    def __init__(self, vocab_size, n_embd, n_head, n_layer, block_size, dropout):
        super().__init__()
        self.block_size = block_size
        self.token_embedding = nn.Embedding(vocab_size, n_embd)
        self.position_embedding = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[
            Block(n_embd, n_head, block_size, dropout) for _ in range(n_layer)
        ])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_embedding(idx)
        pos_emb = self.position_embedding(torch.arange(T, device=idx.device))
        x = tok_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B * T, C), targets.view(B * T))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=0.8, top_k=40):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, idx_next], dim=1)
        return idx


model = GPT(VOCAB_SIZE, N_EMBD, N_HEAD, N_LAYER, BLOCK_SIZE, DROPOUT).to(DEVICE)
n_params = sum(p.numel() for p in model.parameters())
print(f"\nПараметров в модели: {n_params:,}")

optimizer = torch.optim.AdamW(model.parameters(), lr=LR)


# ============ ОБУЧЕНИЕ ============
@torch.no_grad()
def estimate_loss():
    model.eval()
    out = {}
    for name, dl in [("train", train_dl), ("val", val_dl)]:
        losses = []
        for x, y in dl:
            x, y = x.to(DEVICE), y.to(DEVICE)
            _, loss = model(x, y)
            losses.append(loss.item())
        out[name] = sum(losses) / len(losses)
    model.train()
    return out


print("\nНачинаю обучение...")
start = time.time()

for epoch in range(EPOCHS):
    for step, (x, y) in enumerate(train_dl):
        x, y = x.to(DEVICE), y.to(DEVICE)
        logits, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        if step % 200 == 0:
            print(f"epoch {epoch+1}/{EPOCHS}  step {step}/{len(train_dl)}  loss {loss.item():.4f}")

    metrics = estimate_loss()
    elapsed = time.time() - start
    print(f"=== ЭПОХА {epoch+1}: train {metrics['train']:.4f}, val {metrics['val']:.4f}, "
          f"время {elapsed:.0f}с ===")

# ============ СОХРАНЕНИЕ ============
torch.save({
    "model_state": model.state_dict(),
    "config": {
        "vocab_size": VOCAB_SIZE,
        "n_embd": N_EMBD,
        "n_head": N_HEAD,
        "n_layer": N_LAYER,
        "block_size": BLOCK_SIZE,
        "dropout": DROPOUT,
    }
}, MODEL_PATH)

print(f"\n✅ Модель сохранена: {MODEL_PATH}")

# ============ ТЕСТ ГЕНЕРАЦИИ ============
print("\n--- Пробуем сгенерировать ---")

inv_vocab = {v: k for k, v in vocab.items()}

def encode(text):
    return [vocab["<BOS>"]] + [vocab.get(c, vocab["<UNK>"]) for c in text]

def decode(ids):
    return "".join(inv_vocab.get(i, "?") for i in ids)

for prompt in ["<ОН> ", "<Я> ", "<ОН> привет", "<ОН> бодя"]:
    ids = torch.tensor([encode(prompt)], dtype=torch.long).to(DEVICE)
    out = model.generate(ids, max_new_tokens=80, temperature=0.8, top_k=40)
    text = decode(out[0].tolist())
    print(f"\nПромпт: {prompt}")
    print(f"Ответ:  {text}")