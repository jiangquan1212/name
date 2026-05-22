"""
深度学习期末作业：基于CNN和LSTM的病毒/细菌DNA序列分类
使用Biopython下载数据（带重试机制）
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, GlobalMaxPooling1D, LSTM, Bidirectional
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.regularizers import l2
from Bio import Entrez, SeqIO
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置随机种子
np.random.seed(42)
tf.random.set_seed(42)

# ========== NCBI Entrez配置 ==========
Entrez.email = "your_email@example.com"  # 请替换为你的邮箱
Entrez.tool = "DeepLearningHomework"

# 增加超时时间和重试次数
import socket
import urllib.request
socket.setdefaulttimeout(60)  # 设置60秒超时

print("=" * 60)
print("DNA序列分类系统 - 病毒 vs 细菌")
print("=" * 60)


# ==================== 第一部分：下载数据 ====================
print("\n[步骤1] 从NCBI下载序列数据...")

def download_with_retry(search_term, output_file, max_records=200, max_retries=3):
    """
    带重试机制的下载函数
    """
    for attempt in range(max_retries):
        try:
            print(f"  尝试 {attempt + 1}/{max_retries}: {search_term}")

            # 搜索
            handle = Entrez.esearch(
                db="nucleotide",
                term=search_term,
                retmax=max_records,
                usehistory="y"
            )
            search_results = Entrez.read(handle)
            handle.close()

            id_list = search_results["IdList"]

            if not id_list:
                print(f"  ⚠️ 未找到序列")
                return None

            print(f"  ✅ 找到 {len(id_list)} 条序列，开始下载...")

            # 下载
            handle = Entrez.efetch(
                db="nucleotide",
                id=id_list,
                rettype="fasta",
                retmode="text"
            )
            fasta_data = handle.read()
            handle.close()

            # 保存
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(fasta_data)

            print(f"  ✅ 保存至: {output_file}")
            return output_file

        except Exception as e:
            print(f"  ❌ 尝试 {attempt + 1} 失败: {e}")
            if attempt < max_retries - 1:
                wait_time = 30 * (attempt + 1)
                print(f"  等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ 下载失败: {search_term}")
                return None


# 下载病毒数据
print("\n" + "="*40)
print("下载病毒数据：SARS-CoV-2")
print("="*40)

virus_file = download_with_retry(
    search_term='txid2697049[Organism] AND "complete genome"[Title]',
    output_file="sars_cov_2.fasta",
    max_records=200
)

# 下载细菌数据
print("\n" + "="*40)
print("下载细菌数据：Escherichia coli 16S rRNA")
print("="*40)

bacteria_file = download_with_retry(
    search_term='"16S rRNA"[Title] AND "Escherichia coli"[Organism]',
    output_file="ecoli_16s.fasta",
    max_records=200
)


# ==================== 第二部分：加载数据 ====================
print("\n[步骤2] 加载序列数据...")

def load_fasta_sequences(fasta_path, label, max_len=1000, max_seq=200):
    """从FASTA文件加载序列"""
    sequences = []
    labels = []

    if not fasta_path or not os.path.exists(fasta_path):
        print(f"⚠️ 文件不存在: {fasta_path}")
        return sequences, labels

    for i, record in enumerate(SeqIO.parse(fasta_path, "fasta")):
        if i >= max_seq:
            break
        seq = str(record.seq).upper()
        seq = ''.join([b for b in seq if b in 'ATCG'])
        if len(seq) >= 100:
            sequences.append(seq[:max_len])
            labels.append(label)

    print(f"  {os.path.basename(fasta_path)}: {len(sequences)} 条 (标签={label})")
    return sequences, labels


# 加载数据
virus_seqs, virus_labels = load_fasta_sequences(virus_file, label=1, max_seq=200)
bacteria_seqs, bacteria_labels = load_fasta_sequences(bacteria_file, label=0, max_seq=200)

# 如果下载失败，生成模拟数据
if len(virus_seqs) == 0 or len(bacteria_seqs) == 0:
    print("\n⚠️ 使用模拟数据替代...")

    def generate_mock_data(n, seq_type):
        bases = ['A', 'T', 'C', 'G']
        if seq_type == 'virus':
            probs = [0.35, 0.35, 0.15, 0.15]
        else:
            probs = [0.25, 0.25, 0.25, 0.25]
        return [''.join(np.random.choice(bases, size=1000, p=probs)) for _ in range(n)]

    if len(virus_seqs) == 0:
        virus_seqs = generate_mock_data(200, 'virus')
        virus_labels = [1] * 200
        print(f"  生成模拟病毒数据: 200条")

    if len(bacteria_seqs) == 0:
        bacteria_seqs = generate_mock_data(200, 'bacteria')
        bacteria_labels = [0] * 200
        print(f"  生成模拟细菌数据: 200条")

# 确保数量均衡
n_samples = min(len(virus_seqs), len(bacteria_seqs))
virus_seqs = virus_seqs[:n_samples]
bacteria_seqs = bacteria_seqs[:n_samples]
virus_labels = virus_labels[:n_samples]
bacteria_labels = bacteria_labels[:n_samples]

X_sequences = virus_seqs + bacteria_seqs
y_labels = virus_labels + bacteria_labels

print(f"\n✅ 病毒: {n_samples} 条, 细菌: {n_samples} 条, 总计: {len(X_sequences)} 条")


# ==================== 第三部分：One-Hot编码 ====================
print("\n[步骤3] One-Hot编码...")

def one_hot_encode(sequences, max_len=1000):
    base_to_idx = {'A':0, 'T':1, 'C':2, 'G':3}
    encoded = np.zeros((len(sequences), max_len, 4))
    for i, seq in enumerate(sequences):
        for j, base in enumerate(seq[:max_len]):
            if base in base_to_idx:
                encoded[i, j, base_to_idx[base]] = 1
    return encoded

X = one_hot_encode(X_sequences, 1000)
y = np.array(y_labels)
print(f"数据形状: {X.shape}")

# 划分数据集
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
print(f"训练集: {X_train.shape[0]}, 验证集: {X_val.shape[0]}, 测试集: {X_test.shape[0]}")


# ==================== 第四部分：构建模型 ====================
print("\n[步骤4] 构建模型...")

def build_cnn():
    model = Sequential([
        Input(shape=(1000,4)),
        Conv1D(128,5,activation='relu',padding='same'),
        BatchNormalization(),
        MaxPooling1D(2),
        Conv1D(64,3,activation='relu',padding='same'),
        BatchNormalization(),
        MaxPooling1D(2),
        Conv1D(32,3,activation='relu',padding='same'),
        BatchNormalization(),
        GlobalMaxPooling1D(),
        Dense(64,activation='relu',kernel_regularizer=l2(0.001)),
        Dropout(0.5),
        Dense(32,activation='relu',kernel_regularizer=l2(0.001)),
        Dropout(0.3),
        Dense(1,activation='sigmoid')
    ])
    return model

def build_lstm():
    model = Sequential([
        Input(shape=(1000,4)),
        Bidirectional(LSTM(128,return_sequences=True,dropout=0.2)),
        BatchNormalization(),
        Bidirectional(LSTM(64,dropout=0.2)),
        BatchNormalization(),
        Dense(64,activation='relu',kernel_regularizer=l2(0.001)),
        Dropout(0.5),
        Dense(32,activation='relu',kernel_regularizer=l2(0.001)),
        Dropout(0.3),
        Dense(1,activation='sigmoid')
    ])
    return model

cnn = build_cnn()
cnn.compile(optimizer=Adam(0.001), loss='binary_crossentropy', metrics=['accuracy'])

lstm = build_lstm()
lstm.compile(optimizer=Adam(0.001), loss='binary_crossentropy', metrics=['accuracy'])

print(f"CNN参数量: {cnn.count_params():,}")
print(f"LSTM参数量: {lstm.count_params():,}")


# ==================== 第五部分：训练 ====================
print("\n[步骤5] 训练模型...")

callbacks = [
    EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
]

print("\n训练CNN...")
hist_cnn = cnn.fit(X_train, y_train, validation_data=(X_val, y_val),
                   epochs=40, batch_size=32, callbacks=callbacks, verbose=1)

print("\n训练LSTM...")
hist_lstm = lstm.fit(X_train, y_train, validation_data=(X_val, y_val),
                     epochs=40, batch_size=32, callbacks=callbacks, verbose=1)


# ==================== 第六部分：评估 ====================
print("\n[步骤6] 评估结果...")

def evaluate(m, name):
    pred = (m.predict(X_test) > 0.5).astype(int)
    return {
        'name': name,
        'acc': accuracy_score(y_test, pred),
        'prec': precision_score(y_test, pred),
        'rec': recall_score(y_test, pred),
        'f1': f1_score(y_test, pred),
        'cm': confusion_matrix(y_test, pred)
    }

res_cnn = evaluate(cnn, "CNN")
res_lstm = evaluate(lstm, "BiLSTM")

print("\n" + "="*50)
print("模型性能对比")
print("="*50)
print(f"{'模型':<10} {'准确率':<10} {'精确率':<10} {'召回率':<10} {'F1分数':<10}")
print("-"*50)
print(f"{res_cnn['name']:<10} {res_cnn['acc']:<10.4f} {res_cnn['prec']:<10.4f} {res_cnn['rec']:<10.4f} {res_cnn['f1']:<10.4f}")
print(f"{res_lstm['name']:<10} {res_lstm['acc']:<10.4f} {res_lstm['prec']:<10.4f} {res_lstm['rec']:<10.4f} {res_lstm['f1']:<10.4f}")


# ==================== 第七部分：可视化 ====================
print("\n[步骤7] 生成图表...")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# 损失曲线
axes[0,0].plot(hist_cnn.history['loss'], label='CNN Train')
axes[0,0].plot(hist_cnn.history['val_loss'], label='CNN Val')
axes[0,0].plot(hist_lstm.history['loss'], label='LSTM Train')
axes[0,0].plot(hist_lstm.history['val_loss'], label='LSTM Val')
axes[0,0].set_title('损失曲线')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# 准确率曲线
axes[0,1].plot(hist_cnn.history['accuracy'], label='CNN Train')
axes[0,1].plot(hist_cnn.history['val_accuracy'], label='CNN Val')
axes[0,1].plot(hist_lstm.history['accuracy'], label='LSTM Train')
axes[0,1].plot(hist_lstm.history['val_accuracy'], label='LSTM Val')
axes[0,1].set_title('准确率曲线')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# 性能对比
metrics = ['Accuracy', 'Precision', 'Recall', 'F1']
cnn_scores = [res_cnn['acc'], res_cnn['prec'], res_cnn['rec'], res_cnn['f1']]
lstm_scores = [res_lstm['acc'], res_lstm['prec'], res_lstm['rec'], res_lstm['f1']]
x = np.arange(4)
axes[0,2].bar(x-0.2, cnn_scores, 0.4, label='CNN', color='steelblue')
axes[0,2].bar(x+0.2, lstm_scores, 0.4, label='BiLSTM', color='coral')
axes[0,2].set_title('性能对比')
axes[0,2].set_xticks(x)
axes[0,2].set_xticklabels(metrics)
axes[0,2].legend()
axes[0,2].set_ylim([0,1])

# 混淆矩阵
sns.heatmap(res_cnn['cm'], annot=True, fmt='d', cmap='Blues', ax=axes[1,0],
            xticklabels=['细菌','病毒'], yticklabels=['细菌','病毒'])
axes[1,0].set_title('CNN混淆矩阵')

sns.heatmap(res_lstm['cm'], annot=True, fmt='d', cmap='Reds', ax=axes[1,1],
            xticklabels=['细菌','病毒'], yticklabels=['细菌','病毒'])
axes[1,1].set_title('BiLSTM混淆矩阵')

# 参数量
axes[1,2].bar(['CNN', 'BiLSTM'], [cnn.count_params(), lstm.count_params()], color=['steelblue','coral'])
axes[1,2].set_title('参数量对比')
for i,v in enumerate([cnn.count_params(), lstm.count_params()]):
    axes[1,2].text(i, v+1000, f'{v:,}', ha='center')

plt.tight_layout()
plt.savefig('result.png', dpi=300)
plt.show()

# 保存模型
cnn.save('cnn_model.h5')
lstm.save('lstm_model.h5')
print("\n✅ 模型已保存")

print("\n" + "="*60)
print("实验完成！")
print("="*60)