import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
from Bio import SeqIO
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置随机种子
np.random.seed(42)
tf.random.set_seed(42)

print("=" * 60)
print("DNA序列分类系统 - 病毒 vs 细菌")
print("使用本地FASTA文件")
print("=" * 60)

# ==================== 第一部分：加载本地FASTA文件 ====================
print("\n[步骤1] 从本地FASTA文件加载序列数据...")


def load_fasta_sequences(fasta_path, label, max_len=1000, max_seq=300):
    """
    从FASTA文件加载序列

    参数:
        fasta_path: FASTA文件路径
        label: 标签（1=病毒，0=细菌）
        max_len: 最大序列长度
        max_seq: 最大加载数量
    """
    sequences = []
    labels = []

    if not os.path.exists(fasta_path):
        print(f"⚠️ 文件不存在: {fasta_path}")
        print(f"   请将文件放到: {os.path.abspath(fasta_path)}")
        return sequences, labels

    for i, record in enumerate(SeqIO.parse(fasta_path, "fasta")):
        if i >= max_seq:
            break
        seq = str(record.seq).upper()
        # 只保留A、T、C、G
        seq = ''.join([b for b in seq if b in 'ATCG'])
        if len(seq) >= 100:
            sequences.append(seq[:max_len])
            labels.append(label)

    print(f"  ✓ {os.path.basename(fasta_path)}: {len(sequences)} 条序列 (标签={label})")
    return sequences, labels


# ========== 请在这里设置你的文件路径 ==========
# 方式1：将文件放在当前目录下，直接写文件名
virus_file = "D:\PythonProject2\sars_cov_2.fasta"  # 病毒数据文件
bacteria_file = "D:\PythonProject2\ecoli_16s.fasta"  # 细菌数据文件
# ========== 检查文件是否存在 ==========
print("\n检查数据文件...")
print(f"病毒文件: {virus_file}")
if os.path.exists(virus_file):
    print(f"  ✅ 存在 ({os.path.getsize(virus_file):,} 字节)")
else:
    print(f"  ❌ 不存在")
    print(f"\n请先下载病毒数据：")
    print(f"  1. 访问 https://ngdc.cncb.ac.cn/ncov/")
    print(f"  2. 点击'序列'标签，筛选SARS-CoV-2")
    print(f"  3. 下载FASTA格式")
    print(f"  4. 保存为: {virus_file}")

print(f"\n细菌文件: {bacteria_file}")
if os.path.exists(bacteria_file):
    print(f"  ✅ 存在 ({os.path.getsize(bacteria_file):,} 字节)")
else:
    print(f"  ❌ 不存在")
    print(f"\n请先下载细菌数据：")
    print(f"  1. 访问 https://ngdc.cncb.ac.cn/genbase/search")
    print(f"  2. 搜索 'Escherichia coli 16S rRNA'")
    print(f"  3. 下载FASTA格式")
    print(f"  4. 保存为: {bacteria_file}")

# ========== 加载数据 ==========
print("\n加载序列数据...")
virus_seqs, virus_labels = load_fasta_sequences(virus_file, label=1, max_seq=300)
bacteria_seqs, bacteria_labels = load_fasta_sequences(bacteria_file, label=0, max_seq=300)

# 如果文件不存在，生成模拟数据
if len(virus_seqs) == 0 or len(bacteria_seqs) == 0:
    print("\n⚠️ 未找到数据文件，使用模拟数据替代...")


    def generate_mock_data(n, seq_type):
        """生成模拟DNA序列"""
        bases = ['A', 'T', 'C', 'G']
        if seq_type == 'virus':
            # 病毒序列：A/T含量高
            probs = [0.35, 0.35, 0.15, 0.15]
        else:
            # 细菌序列：均匀分布
            probs = [0.25, 0.25, 0.25, 0.25]
        return [''.join(np.random.choice(bases, size=1000, p=probs)) for _ in range(n)]


    if len(virus_seqs) == 0:
        virus_seqs = generate_mock_data(300, 'virus')
        virus_labels = [1] * 300
        print(f"  ✓ 生成模拟病毒数据: 300条")

    if len(bacteria_seqs) == 0:
        bacteria_seqs = generate_mock_data(300, 'bacteria')
        bacteria_labels = [0] * 300
        print(f"  ✓ 生成模拟细菌数据: 300条")

# 确保两类数据数量均衡
n_samples = min(len(virus_seqs), len(bacteria_seqs))
virus_seqs = virus_seqs[:n_samples]
bacteria_seqs = bacteria_seqs[:n_samples]
virus_labels = virus_labels[:n_samples]
bacteria_labels = bacteria_labels[:n_samples]

# 合并数据
X_sequences = virus_seqs + bacteria_seqs
y_labels = virus_labels + bacteria_labels

print(f"\n✅ 最终数据集统计:")
print(f"   病毒样本: {n_samples} 条")
print(f"   细菌样本: {n_samples} 条")
print(f"   总样本数: {len(X_sequences)} 条")

# ==================== 第二部分：One-Hot编码 ====================
print("\n[步骤2] One-Hot编码...")


def one_hot_encode(sequences, max_len=1000):
    """One-Hot编码DNA序列"""
    base_to_idx = {'A': 0, 'T': 1, 'C': 2, 'G': 3}
    encoded = np.zeros((len(sequences), max_len, 4))

    for i, seq in enumerate(sequences):
        for j, base in enumerate(seq[:max_len]):
            if base in base_to_idx:
                encoded[i, j, base_to_idx[base]] = 1

    return encoded


X = one_hot_encode(X_sequences, max_len=1000)
y = np.array(y_labels)
print(f"输入数据形状: {X.shape}")
print(f"标签形状: {y.shape}")

# 划分数据集
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

print(f"\n数据集划分:")
print(f"  训练集: {X_train.shape[0]} 样本")
print(f"  验证集: {X_val.shape[0]} 样本")
print(f"  测试集: {X_test.shape[0]} 样本")

# ==================== 第三部分：构建模型 ====================
print("\n[步骤3] 构建CNN和LSTM模型...")


def build_cnn_model(input_shape=(1000, 4)):
    """构建1D CNN模型"""
    model = Sequential([
        Input(shape=input_shape),

        # 第一层卷积
        Conv1D(filters=128, kernel_size=5, activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),

        # 第二层卷积
        Conv1D(filters=64, kernel_size=3, activation='relu', padding='same'),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),

        # 第三层卷积
        Conv1D(filters=32, kernel_size=3, activation='relu', padding='same'),
        BatchNormalization(),
        GlobalMaxPooling1D(),

        # 全连接层
        Dense(64, activation='relu', kernel_regularizer=l2(0.001)),
        Dropout(0.5),
        Dense(32, activation='relu', kernel_regularizer=l2(0.001)),
        Dropout(0.3),

        # 输出层
        Dense(1, activation='sigmoid')
    ])
    return model


def build_lstm_model(input_shape=(1000, 4)):
    """构建双向LSTM模型"""
    model = Sequential([
        Input(shape=input_shape),

        # 第一层双向LSTM
        Bidirectional(LSTM(128, return_sequences=True, dropout=0.2, recurrent_dropout=0.2)),
        BatchNormalization(),

        # 第二层双向LSTM
        Bidirectional(LSTM(64, dropout=0.2, recurrent_dropout=0.2)),
        BatchNormalization(),

        # 全连接层
        Dense(64, activation='relu', kernel_regularizer=l2(0.001)),
        Dropout(0.5),
        Dense(32, activation='relu', kernel_regularizer=l2(0.001)),
        Dropout(0.3),

        # 输出层
        Dense(1, activation='sigmoid')
    ])
    return model


# 创建模型
cnn_model = build_cnn_model()
cnn_model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

lstm_model = build_lstm_model()
lstm_model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"CNN模型参数量: {cnn_model.count_params():,}")
print(f"LSTM模型参数量: {lstm_model.count_params():,}")

# ==================== 第四部分：训练模型 ====================
print("\n[步骤4] 训练模型...")

# 回调函数
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=1
    )
]

# 训练CNN模型
print("\n" + "=" * 40)
print("训练CNN模型...")
print("=" * 40)

cnn_history = cnn_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

# 训练LSTM模型
print("\n" + "=" * 40)
print("训练LSTM模型...")
print("=" * 40)

lstm_history = lstm_model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

# ==================== 第五部分：模型评估 ====================
print("\n[步骤5] 模型评估...")


def evaluate_model(model, model_name, X_test, y_test):
    """评估模型性能"""
    # 预测
    y_pred_prob = model.predict(X_test)
    y_pred = (y_pred_prob > 0.5).astype(int)

    # 计算指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"\n{model_name} 性能指标:")
    print(f"  准确率 (Accuracy):  {accuracy:.4f}")
    print(f"  精确率 (Precision): {precision:.4f}")
    print(f"  召回率 (Recall):    {recall:.4f}")
    print(f"  F1分数 (F1-Score):  {f1:.4f}")

    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred)

    return {
        'name': model_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm
    }


cnn_results = evaluate_model(cnn_model, "CNN", X_test, y_test)
lstm_results = evaluate_model(lstm_model, "BiLSTM", X_test, y_test)

# ==================== 第六部分：可视化对比 ====================
print("\n[步骤6] 生成可视化对比图表...")

# 创建大图
fig = plt.figure(figsize=(16, 12))

# 1. 训练损失曲线对比
ax1 = plt.subplot(2, 3, 1)
ax1.plot(cnn_history.history['loss'], label='CNN Train Loss', linewidth=2)
ax1.plot(cnn_history.history['val_loss'], label='CNN Val Loss', linewidth=2, linestyle='--')
ax1.plot(lstm_history.history['loss'], label='LSTM Train Loss', linewidth=2)
ax1.plot(lstm_history.history['val_loss'], label='LSTM Val Loss', linewidth=2, linestyle='--')
ax1.set_xlabel('Epoch', fontsize=12)
ax1.set_ylabel('Loss', fontsize=12)
ax1.set_title('训练损失对比曲线', fontsize=14)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. 训练准确率曲线对比
ax2 = plt.subplot(2, 3, 2)
ax2.plot(cnn_history.history['accuracy'], label='CNN Train Acc', linewidth=2)
ax2.plot(cnn_history.history['val_accuracy'], label='CNN Val Acc', linewidth=2, linestyle='--')
ax2.plot(lstm_history.history['accuracy'], label='LSTM Train Acc', linewidth=2)
ax2.plot(lstm_history.history['val_accuracy'], label='LSTM Val Acc', linewidth=2, linestyle='--')
ax2.set_xlabel('Epoch', fontsize=12)
ax2.set_ylabel('Accuracy', fontsize=12)
ax2.set_title('训练准确率对比曲线', fontsize=14)
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. 性能指标对比柱状图
ax3 = plt.subplot(2, 3, 3)
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
cnn_scores = [cnn_results['accuracy'], cnn_results['precision'],
              cnn_results['recall'], cnn_results['f1']]
lstm_scores = [lstm_results['accuracy'], lstm_results['precision'],
               lstm_results['recall'], lstm_results['f1']]

x = np.arange(len(metrics))
width = 0.35
bars1 = ax3.bar(x - width / 2, cnn_scores, width, label='CNN', color='steelblue')
bars2 = ax3.bar(x + width / 2, lstm_scores, width, label='BiLSTM', color='coral')
ax3.set_xlabel('评估指标', fontsize=12)
ax3.set_ylabel('分数', fontsize=12)
ax3.set_title('模型性能指标对比', fontsize=14)
ax3.set_xticks(x)
ax3.set_xticklabels(metrics)
ax3.legend()
ax3.set_ylim([0, 1.05])

# 添加数值标签
for bar in bars1:
    height = bar.get_height()
    ax3.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
for bar in bars2:
    height = bar.get_height()
    ax3.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

# 4. CNN混淆矩阵
ax4 = plt.subplot(2, 3, 4)
cm_cnn = cnn_results['confusion_matrix']
sns.heatmap(cm_cnn, annot=True, fmt='d', cmap='Blues', ax=ax4,
            xticklabels=['细菌', '病毒'], yticklabels=['细菌', '病毒'])
ax4.set_xlabel('预测标签', fontsize=12)
ax4.set_ylabel('真实标签', fontsize=12)
ax4.set_title('CNN混淆矩阵', fontsize=14)

# 5. LSTM混淆矩阵
ax5 = plt.subplot(2, 3, 5)
cm_lstm = lstm_results['confusion_matrix']
sns.heatmap(cm_lstm, annot=True, fmt='d', cmap='Reds', ax=ax5,
            xticklabels=['细菌', '病毒'], yticklabels=['细菌', '病毒'])
ax5.set_xlabel('预测标签', fontsize=12)
ax5.set_ylabel('真实标签', fontsize=12)
ax5.set_title('BiLSTM混淆矩阵', fontsize=14)

# 6. 模型参数量对比
ax6 = plt.subplot(2, 3, 6)
cnn_params = cnn_model.count_params()
lstm_params = lstm_model.count_params()
ax6.bar(['CNN', 'BiLSTM'], [cnn_params, lstm_params], color=['steelblue', 'coral'])
ax6.set_ylabel('参数量', fontsize=12)
ax6.set_title('模型复杂度对比', fontsize=14)

# 添加数值标签
ax6.text(0, cnn_params + 1000, f'{cnn_params:,}', ha='center', va='bottom')
ax6.text(1, lstm_params + 1000, f'{lstm_params:,}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('model_comparison_results.png', dpi=300, bbox_inches='tight')
plt.show()

# ==================== 第七部分：最终报告 ====================
print("\n" + "=" * 60)
print("最终实验结果报告")
print("=" * 60)

# 创建结果对比表
results_df = pd.DataFrame({
    '模型': ['CNN', 'BiLSTM'],
    '准确率': [cnn_results['accuracy'], lstm_results['accuracy']],
    '精确率': [cnn_results['precision'], lstm_results['precision']],
    '召回率': [cnn_results['recall'], lstm_results['recall']],
    'F1分数': [cnn_results['f1'], lstm_results['f1']],
    '参数量': [cnn_model.count_params(), lstm_model.count_params()]
})

print("\n模型性能对比表:")
print(results_df.to_string(index=False))

# 确定最佳模型
if cnn_results['accuracy'] > lstm_results['accuracy']:
    best_model = "CNN"
    best_accuracy = cnn_results['accuracy']
else:
    best_model = "BiLSTM"
    best_accuracy = lstm_results['accuracy']

print(f"\n🏆 最佳模型: {best_model} (准确率: {best_accuracy:.4f})")

# 保存模型
cnn_model.save('cnn_dna_classifier.h5')
lstm_model.save('lstm_dna_classifier.h5')
print("\n✅ 模型已保存:")
print("   - cnn_dna_classifier.h5")
print("   - lstm_dna_classifier.h5")

print("\n" + "=" * 60)
print("实验完成！")
print("=" * 60)