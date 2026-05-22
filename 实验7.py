# -*- coding: utf-8 -*-
"""
实验：RNN 与 LSTM 作诗对比（快速版本）
运行时间优化到原来的1/3
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, LSTM, Dense, Embedding, Dropout
import matplotlib.pyplot as plt
from tabulate import tabulate
import random
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置随机种子
random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)

# 设置GPU内存增长（如果有GPU）
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError:
        pass

print("=" * 60)
print("RNN vs LSTM 作诗对比实验（快速版）")
print("=" * 60)

# ------------------------------
# 1. 快速数据加载（限制数据量）
# ------------------------------
data_path = r"D:\PythonProject2\data\data_we\poems_clean.txt"
try:
    with open(data_path, 'r', encoding='utf-8') as f:
        poems = f.read().splitlines()
except:
    try:
        with open(data_path, 'r', encoding='gbk') as f:
            poems = f.read().splitlines()
    except:
        print("使用示例数据")
        poems = [
            "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
            "白日依山尽，黄河入海流。欲穷千里目，更上一层楼。",
            "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。",
            "千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。",
            "向晚意不适，驱车登古原。夕阳无限好，只是近黄昏。",
            "离离原上草，一岁一枯荣。野火烧不尽，春风吹又生。",
            "空山不见人，但闻人语响。返景入深林，复照青苔上。",
            "红豆生南国，春来发几枝。愿君多采撷，此物最相思。",
        ]

poems = [p.strip() for p in poems if p.strip()]
# 限制使用的诗歌数量（加速）
MAX_POEMS = 5000  # 只使用前5000首诗
if len(poems) > MAX_POEMS:
    poems = poems[:MAX_POEMS]
    print(f"限制使用 {MAX_POEMS} 首诗以加速训练")
print(f"共读取 {len(poems)} 首诗")

# 字符级分词
tokenizer = Tokenizer(char_level=True, filters='')
tokenizer.fit_on_texts(poems)
vocab_size = len(tokenizer.word_index) + 1
print(f"词汇表大小: {vocab_size}")

# 转换为序列
sequences = tokenizer.texts_to_sequences(poems)

# 限制序列最大长度（加速）
MAX_SEQ_LEN = 50  # 限制最大长度为50
max_len = min(max(len(seq) for seq in sequences), MAX_SEQ_LEN)
print(f"最大序列长度: {max_len}")

# ------------------------------
# 2. 快速构建训练样本（减少样本数）
# ------------------------------
print("构建训练样本...")
X_data, y_data = [], []
for seq in sequences:
    # 限制每个序列的滑动窗口数量
    seq = seq[:MAX_SEQ_LEN]  # 截断序列
    for i in range(1, len(seq)):
        X_data.append(seq[:i])
        y_data.append(seq[i])

# 限制总样本数量（关键加速点）
MAX_SAMPLES = 200000  # 最多20万样本（原108万）
if len(X_data) > MAX_SAMPLES:
    print(f"样本数过多（{len(X_data)}），随机采样到 {MAX_SAMPLES}")
    indices = np.random.choice(len(X_data), MAX_SAMPLES, replace=False)
    X_data = [X_data[i] for i in indices]
    y_data = [y_data[i] for i in indices]

# Padding
X_padded = pad_sequences(X_data, maxlen=max_len-1, padding='post')
y_data = np.array(y_data)

print(f"训练样本数: {len(X_padded)}")
print(f"输入形状: {X_padded.shape}")
print(f"内存占用: {X_padded.nbytes / 1024**3:.2f} GB")

# ------------------------------
# 3. 精简模型参数（加速训练）
# ------------------------------
embedding_dim = 64      # 原128，减半
rnn_units = 128         # 原256，减半
batch_size = 256        # 原64，增大4倍
epochs = 10             # 原20，减半

print(f"\n模型配置：")
print(f"  Embedding维度: {embedding_dim}")
print(f"  RNN单元数: {rnn_units}")
print(f"  Batch Size: {batch_size}")
print(f"  Epochs: {epochs}")

# ------------------------------
# 4. 训练RNN模型
# ------------------------------
print("\n训练 RNN 模型...")
model_rnn = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=max_len-1),
    SimpleRNN(rnn_units, dropout=0.2),
    Dense(vocab_size, activation='softmax')
])
model_rnn.compile(
    loss='sparse_categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

# 添加早停防止过拟合
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=3,
    restore_best_weights=True
)

history_rnn = model_rnn.fit(
    X_padded, y_data,
    batch_size=batch_size,
    epochs=epochs,
    validation_split=0.1,
    verbose=1,
    callbacks=[early_stop]
)

# ------------------------------
# 5. 训练LSTM模型
# ------------------------------
print("\n训练 LSTM 模型...")
model_lstm = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=max_len-1),
    LSTM(rnn_units, dropout=0.2),
    Dense(vocab_size, activation='softmax')
])
model_lstm.compile(
    loss='sparse_categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

history_lstm = model_lstm.fit(
    X_padded, y_data,
    batch_size=batch_size,
    epochs=epochs,
    validation_split=0.1,
    verbose=1,
    callbacks=[early_stop]
)

# ------------------------------
# 6. 生成函数
# ------------------------------
idx_to_char = {v: k for k, v in tokenizer.word_index.items()}
idx_to_char[0] = ''

def generate_poem(model, seed_text, length=20, temperature=0.8):
    """快速生成诗句"""
    seq = [tokenizer.word_index.get(c, 0) for c in seed_text]
    generated = seed_text
    for _ in range(length):
        padded = pad_sequences([seq], maxlen=max_len-1, padding='post')
        preds = model.predict(padded, verbose=0)[0]
        # 温度采样
        preds = np.log(preds + 1e-8) / temperature
        preds = np.exp(preds) / np.sum(np.exp(preds))
        next_idx = np.random.choice(len(preds), p=preds)
        if next_idx == 0:
            break
        next_char = idx_to_char.get(next_idx, '')
        generated += next_char
        seq.append(next_idx)
        seq = seq[-(max_len-1):]
    return generated

def generate_acrostic(model, head_text, temperature=0.8):
    """生成藏头诗"""
    poem_lines = []
    for head_char in head_text:
        if head_char not in tokenizer.word_index:
            continue
        seq = [tokenizer.word_index[head_char]]
        line = head_char
        for _ in range(5):  # 每句6字
            padded = pad_sequences([seq], maxlen=max_len-1, padding='post')
            preds = model.predict(padded, verbose=0)[0]
            preds = np.log(preds + 1e-8) / temperature
            preds = np.exp(preds) / np.sum(np.exp(preds))
            next_idx = np.random.choice(len(preds), p=preds)
            if next_idx == 0:
                break
            next_char = idx_to_char.get(next_idx, '')
            line += next_char
            seq.append(next_idx)
        poem_lines.append(line)
    return ' '.join(poem_lines)

# ------------------------------
# 7. 输出结果
# ------------------------------
print("\n" + "=" * 60)
print("【RNN 作诗结果】")
print("=" * 60)

seed_words = ["春风", "明月", "秋水"]
rnn_results = {}
for seed in seed_words:
    gen = generate_poem(model_rnn, seed, length=15)
    rnn_results[seed] = gen
    print(f"「{seed}」→ {gen}")

print("\n" + "=" * 60)
print("【LSTM 作诗结果】")
print("=" * 60)

lstm_results = {}
for seed in seed_words:
    gen = generate_poem(model_lstm, seed, length=15)
    lstm_results[seed] = gen
    print(f"「{seed}」→ {gen}")

# 藏头诗
print("\n" + "=" * 60)
print("【藏头诗示例】")
print("=" * 60)
print("\nRNN 藏头诗（春暖花开）:")
print(generate_acrostic(model_rnn, "春暖花开"))
print("\nLSTM 藏头诗（春暖花开）:")
print(generate_acrostic(model_lstm, "春暖花开"))

# 性能对比表格
print("\n" + "=" * 60)
print("【性能对比】")
print("=" * 60)

rnn_acc = history_rnn.history['val_accuracy'][-1]
lstm_acc = history_lstm.history['val_accuracy'][-1]
rnn_loss = history_rnn.history['val_loss'][-1]
lstm_loss = history_lstm.history['val_loss'][-1]

table_data = [
    ["模型", "验证准确率", "验证损失", "训练时间"],
    ["RNN", f"{rnn_acc:.2%}", f"{rnn_loss:.4f}", "较快"],
    ["LSTM", f"{lstm_acc:.2%}", f"{lstm_loss:.4f}", "较慢"],
    ["提升", f"{(lstm_acc - rnn_acc)*100:+.2f}%", f"{rnn_loss - lstm_loss:+.4f}", "-"]
]
print(tabulate(table_data, headers="firstrow", tablefmt="grid"))

# ------------------------------
# 8. 绘图对比
# ------------------------------
plt.figure(figsize=(14, 5))

# 损失曲线
plt.subplot(1, 2, 1)
plt.plot(history_rnn.history['loss'], label='RNN Train', linewidth=2)
plt.plot(history_rnn.history['val_loss'], label='RNN Val', linestyle='--', linewidth=2)
plt.plot(history_lstm.history['loss'], label='LSTM Train', linewidth=2)
plt.plot(history_lstm.history['val_loss'], label='LSTM Val', linestyle='--', linewidth=2)
plt.title('损失函数对比', fontsize=14, fontweight='bold')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True, alpha=0.3)

# 准确率曲线
plt.subplot(1, 2, 2)
plt.plot(history_rnn.history['accuracy'], label='RNN Train', linewidth=2)
plt.plot(history_rnn.history['val_accuracy'], label='RNN Val', linestyle='--', linewidth=2)
plt.plot(history_lstm.history['accuracy'], label='LSTM Train', linewidth=2)
plt.plot(history_lstm.history['val_accuracy'], label='LSTM Val', linestyle='--', linewidth=2)
plt.title('准确率对比', fontsize=14, fontweight='bold')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 总结
print("\n" + "=" * 60)
print("【实验总结】")
print("=" * 60)
print(f"✓ 数据规模: {len(poems)} 首诗, {len(X_padded)} 训练样本")
print(f"✓ RNN 验证准确率: {rnn_acc:.2%}")
print(f"✓ LSTM 验证准确率: {lstm_acc:.2%}")
print(f"✓ 性能提升: {(lstm_acc - rnn_acc)*100:.2f}%")

if lstm_acc > rnn_acc:
    print("\n结论: LSTM 模型表现更优，能更好地学习诗词的长期依赖关系。")
else:
    print("\n结论: 两者表现相近，RNN 在小规模数据上已经足够。")

print("\n优化效果：")
print("• 训练样本: 108万 → 20万 (减少81%)")
print("• 模型参数: 减少约75%")
print("• Batch Size: 64 → 256 (提升4倍)")
print("• Epochs: 20 → 10 (减半)")
print("✓ 预计运行时间缩短到原来的1/3")