
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from PIL import Image
import os
import warnings

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

warnings.filterwarnings('ignore')

# 设置随机种子
tf.random.set_seed(42)
np.random.seed(42)


# ==================== 第一部分：数据加载与预处理 ====================

def load_local_gesture_data(data_path='D:\PythonProject2\data\gesture', img_size=(64, 64)):
    """
    加载本地手势识别数据集
    目录结构: data_path/类别名/图片文件
    """
    images = []
    labels = []
    class_names = []

    if not os.path.exists(data_path):
        print(f"路径不存在: {data_path}")
        return None, None, None

    print(f"\n加载本地数据: {data_path}")

    for class_idx, class_name in enumerate(sorted(os.listdir(data_path))):
        class_path = os.path.join(data_path, class_name)
        if not os.path.isdir(class_path):
            continue

        class_names.append(class_name)
        print(f"  类别 {class_idx}: {class_name}")

        img_count = 0
        for img_file in os.listdir(class_path):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                img_path = os.path.join(class_path, img_file)
                try:
                    img = Image.open(img_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img = img.resize(img_size)
                    img_array = np.array(img)
                    images.append(img_array)
                    labels.append(class_idx)
                    img_count += 1
                except Exception as e:
                    print(f"    读取失败: {img_file}")

        print(f"    加载了 {img_count} 张图片")

    if len(images) == 0:
        print("未找到任何图片!")
        return None, None, None

    images = np.array(images)
    labels = np.array(labels)

    print(f"\n数据集加载完成:")
    print(f"  总图片数: {len(images)}")
    print(f"  图片尺寸: {images.shape[1:]}")
    print(f"  类别数: {len(class_names)}")
    print(f"  类别: {class_names}")

    return images, labels, class_names


def load_mnist_gesture():
    """使用MNIST数据集模拟手势识别（备选方案）"""
    print("\n使用MNIST数据集模拟手势识别...")
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

    x = np.concatenate([x_train, x_test], axis=0)
    y = np.concatenate([y_train, y_test], axis=0)

    # 归一化
    x = x.astype('float32') / 255.0
    x = np.expand_dims(x, axis=-1)

    # 转换为RGB（3通道）以保持一致性
    x = np.repeat(x, 3, axis=-1)

    class_names = [str(i) for i in range(10)]

    print(f"MNIST数据集加载完成: {x.shape}")
    return x, y, class_names


def create_sample_dataset(output_path="sample_gesture_data", samples_per_class=20):
    """
    创建示例数据集（当没有真实数据时使用）
    生成简单的几何图形作为手势数据
    """
    try:
        import cv2
        has_cv2 = True
    except ImportError:
        has_cv2 = False
        print("警告: 未安装opencv-python，使用PIL创建示例数据")

    gestures = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    img_size = (64, 64)

    for gesture in gestures:
        gesture_path = os.path.join(output_path, gesture)
        os.makedirs(gesture_path, exist_ok=True)

        for i in range(samples_per_class):
            # 创建空白图像
            if has_cv2:
                img = np.ones((img_size[0], img_size[1], 3), dtype=np.uint8) * 255
                center = (32, 32)

                if gesture == "0":
                    cv2.circle(img, center, 20, (0, 0, 0), -1)
                elif gesture == "1":
                    cv2.line(img, (32, 10), (32, 54), (0, 0, 0), 8)
                elif gesture == "2":
                    cv2.line(img, (20, 20), (44, 44), (0, 0, 0), 6)
                    cv2.line(img, (44, 20), (20, 44), (0, 0, 0), 6)
                elif gesture == "3":
                    cv2.rectangle(img, (20, 20), (44, 44), (0, 0, 0), 4)
                else:
                    size = 15 + int(gesture) * 2
                    top_left = (32 - size // 2, 32 - size // 2)
                    bottom_right = (32 + size // 2, 32 + size // 2)
                    cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), -1)

                cv2.imwrite(os.path.join(gesture_path, f"sample_{i}.png"), img)
            else:
                # 使用PIL创建简单图像
                from PIL import ImageDraw
                img = Image.new('RGB', img_size, 'white')
                draw = ImageDraw.Draw(img)

                if gesture == "0":
                    draw.ellipse([20, 20, 44, 44], fill='black')
                elif gesture == "1":
                    draw.line([(32, 10), (32, 54)], fill='black', width=8)
                else:
                    draw.rectangle([20, 20, 44, 44], outline='black', width=4)

                img.save(os.path.join(gesture_path, f"sample_{i}.png"))

    print(f"示例数据集已创建: {output_path}")
    print(f"包含 {len(gestures)} 个类别，每类 {samples_per_class} 张图片")
    return output_path


def preprocess_data(images, labels, test_size=0.2, val_size=0.1):
    """数据预处理和划分"""
    # 归一化
    if images.max() > 1.0:
        images = images.astype('float32') / 255.0

    # 划分数据集
    x_train, x_temp, y_train, y_temp = train_test_split(
        images, labels, test_size=test_size + val_size,
        random_state=42, stratify=labels
    )

    x_val, x_test, y_val, y_test = train_test_split(
        x_temp, y_temp, test_size=test_size / (test_size + val_size),
        random_state=42, stratify=y_temp
    )

    return x_train, x_val, x_test, y_train, y_val, y_test


def data_augmentation():
    """数据增强层"""
    return keras.Sequential([
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        layers.RandomTranslation(0.1, 0.1),
        layers.RandomFlip("horizontal"),
    ])


# ==================== 第二部分：模型定义 ====================

def create_optimized_cnn(input_shape, num_classes):
    """优化版CNN模型"""
    inputs = layers.Input(shape=input_shape)

    x = data_augmentation()(inputs)

    # Block 1
    x = layers.Conv2D(32, 3, padding='same', kernel_regularizer=regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(32, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.25)(x)

    # Block 2
    x = layers.Conv2D(64, 3, padding='same', kernel_regularizer=regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(64, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.25)(x)

    # Block 3
    x = layers.Conv2D(128, 3, padding='same', kernel_regularizer=regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(128, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.25)(x)

    # 全连接层
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    return models.Model(inputs, outputs)


def create_vggnet(input_shape, num_classes):
    """轻量级VGGNet（8个卷积层）"""
    inputs = layers.Input(shape=input_shape)

    x = data_augmentation()(inputs)

    # Block 1
    x = layers.Conv2D(32, 3, padding='same', activation='relu')(x)
    x = layers.Conv2D(32, 3, padding='same', activation='relu')(x)
    x = layers.MaxPooling2D(2)(x)

    # Block 2
    x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
    x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
    x = layers.MaxPooling2D(2)(x)

    # Block 3
    x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
    x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
    x = layers.MaxPooling2D(2)(x)

    # Block 4
    x = layers.Conv2D(256, 3, padding='same', activation='relu')(x)
    x = layers.Conv2D(256, 3, padding='same', activation='relu')(x)
    x = layers.MaxPooling2D(2)(x)

    # 全连接层
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    return models.Model(inputs, outputs)


def residual_block(x, filters, stride=1):
    """残差块"""
    shortcut = x

    x = layers.Conv2D(filters, 3, strides=stride, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(filters, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)

    if stride != 1 or shortcut.shape[-1] != filters:
        shortcut = layers.Conv2D(filters, 1, strides=stride, padding='same')(shortcut)
        shortcut = layers.BatchNormalization()(shortcut)

    x = layers.Add()([x, shortcut])
    x = layers.Activation('relu')(x)

    return x


def create_resnet(input_shape, num_classes):
    """轻量级ResNet"""
    inputs = layers.Input(shape=input_shape)

    x = data_augmentation()(inputs)

    x = layers.Conv2D(32, 3, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = residual_block(x, 32)
    x = residual_block(x, 32)

    x = residual_block(x, 64, stride=2)
    x = residual_block(x, 64)

    x = residual_block(x, 128, stride=2)
    x = residual_block(x, 128)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    return models.Model(inputs, outputs)


# ==================== 第三部分：训练与评估函数 ====================

def compile_and_train(model, x_train, y_train, x_val, y_val,
                      epochs=30, batch_size=64, model_name="model"):
    """编译并训练模型"""

    lr_schedule = keras.optimizers.schedules.ExponentialDecay(
        0.001, decay_steps=1000, decay_rate=0.95, staircase=True
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr_schedule),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    callbacks = [
        keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True, verbose=1),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=4, verbose=1),
        keras.callbacks.ModelCheckpoint(f'{model_name}_best.h5', save_best_only=True, verbose=1)
    ]

    history = model.fit(
        x_train, y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_data=(x_val, y_val),
        callbacks=callbacks,
        verbose=1
    )

    return history


def evaluate_model(model, x_test, y_test, class_names, model_name=""):
    """评估模型"""
    y_pred = np.argmax(model.predict(x_test), axis=1)
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)

    print(f"\n{'=' * 50}")
    print(f"{model_name} 评估结果")
    print(f"{'=' * 50}")
    print(f"测试集准确率: {test_acc:.4f}")
    print(f"测试集损失: {test_loss:.4f}")

    print(f"\n分类报告:")
    print(classification_report(y_test, y_pred, target_names=class_names))

    return test_acc, test_loss, y_pred


def plot_training_history(history, title="训练曲线"):
    """绘制训练曲线（中文标签）"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history.history['accuracy'], label='训练集', marker='o')
    axes[0].plot(history.history['val_accuracy'], label='验证集', marker='s')
    axes[0].set_title(f'{title} - 准确率')
    axes[0].set_xlabel('迭代轮数')
    axes[0].set_ylabel('准确率')
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(history.history['loss'], label='训练集损失', marker='o')
    axes[1].plot(history.history['val_loss'], label='验证集损失', marker='s')
    axes[1].set_title(f'{title} - 损失')
    axes[1].set_xlabel('迭代轮数')
    axes[1].set_ylabel('损失值')
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()


def plot_comparison(histories, names):
    """对比多个模型（中文标签）"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = ['blue', 'red', 'green', 'orange']

    for i, (history, name) in enumerate(zip(histories, names)):
        axes[0].plot(history.history['val_accuracy'], color=colors[i],
                     label=f'{name}', marker='o')
        axes[1].plot(history.history['val_loss'], color=colors[i],
                     label=f'{name}', marker='s')

    axes[0].set_title('模型验证准确率对比')
    axes[0].set_xlabel('迭代轮数')
    axes[0].set_ylabel('准确率')
    axes[0].legend()
    axes[0].grid(True)

    axes[1].set_title('模型验证损失对比')
    axes[1].set_xlabel('迭代轮数')
    axes[1].set_ylabel('损失值')
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()


def plot_confusion_matrix(y_test, y_pred, class_names, title="混淆矩阵"):
    """绘制混淆矩阵（中文标题）"""
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title(title, fontsize=14)
    plt.xlabel('预测标签', fontsize=12)
    plt.ylabel('真实标签', fontsize=12)
    plt.tight_layout()
    plt.show()


def plot_sample_predictions(model, x_test, y_test, class_names, num_samples=9):
    """展示预测样本（中文标题）"""
    predictions = model.predict(x_test[:num_samples])
    pred_classes = np.argmax(predictions, axis=1)

    fig, axes = plt.subplots(3, 3, figsize=(9, 9))
    axes = axes.ravel()

    for i in range(num_samples):
        if x_test[i].shape[-1] == 1:
            axes[i].imshow(x_test[i].squeeze(), cmap='gray')
        else:
            axes[i].imshow(x_test[i])
        axes[i].set_title(f'真实: {class_names[y_test[i]]}\n预测: {class_names[pred_classes[i]]}')
        axes[i].axis('off')

    plt.suptitle('手势识别预测结果示例', fontsize=14)
    plt.tight_layout()
    plt.show()


# ==================== 第四部分：主程序 ====================

def main():
    print("=" * 70)
    print("卷积神经网络手势识别实验")
    print("实验项目（四）和（五）")
    print("=" * 70)

    # ========== 1. 数据加载 ==========
    print("\n【步骤1】数据加载")
    print("-" * 40)

    # 设置数据路径（请修改为你的本地数据路径）
    data_path = r"D:\PythonProject2\data\gesture"

    # 尝试加载本地数据
    images, labels, class_names = load_local_gesture_data(data_path)

    # 如果没有本地数据，创建示例数据
    if images is None:
        print("\n未找到本地数据，创建示例数据集...")
        sample_path = create_sample_dataset("sample_gesture_data", samples_per_class=30)
        images, labels, class_names = load_local_gesture_data(sample_path)

    # 如果还是没有，使用MNIST
    if images is None:
        print("\n使用MNIST数据集作为备选...")
        images, labels, class_names = load_mnist_gesture()

    print(f"\n最终数据集: {images.shape}, 类别数: {len(class_names)}")
    print(f"手势类别: {class_names}")

    # ========== 2. 数据预处理 ==========
    print("\n【步骤2】数据预处理")
    print("-" * 40)

    x_train, x_val, x_test, y_train, y_val, y_test = preprocess_data(images, labels)
    print(f"训练集: {x_train.shape}")
    print(f"验证集: {x_val.shape}")
    print(f"测试集: {x_test.shape}")

    input_shape = x_train.shape[1:]
    num_classes = len(class_names)

    # ========== 3. 训练优化版CNN ==========
    print("\n【步骤3】训练优化版CNN")
    print("-" * 40)

    cnn_model = create_optimized_cnn(input_shape, num_classes)
    cnn_model.summary()

    history_cnn = compile_and_train(cnn_model, x_train, y_train, x_val, y_val,
                                    epochs=20, model_name="optimized_cnn")
    plot_training_history(history_cnn, "优化版CNN")
    acc_cnn, loss_cnn, _ = evaluate_model(cnn_model, x_test, y_test, class_names, "优化版CNN")

    # ========== 4. 训练VGGNet ==========
    print("\n【步骤4】训练VGGNet")
    print("-" * 40)

    vgg_model = create_vggnet(input_shape, num_classes)
    vgg_model.summary()

    history_vgg = compile_and_train(vgg_model, x_train, y_train, x_val, y_val,
                                    epochs=20, model_name="vggnet")
    plot_training_history(history_vgg, "VGGNet")
    acc_vgg, loss_vgg, y_pred_vgg = evaluate_model(vgg_model, x_test, y_test, class_names, "VGGNet")

    # ========== 5. 训练ResNet ==========
    print("\n【步骤5】训练ResNet")
    print("-" * 40)

    resnet_model = create_resnet(input_shape, num_classes)
    resnet_model.summary()

    history_resnet = compile_and_train(resnet_model, x_train, y_train, x_val, y_val,
                                       epochs=20, model_name="resnet")
    plot_training_history(history_resnet, "ResNet")
    acc_resnet, loss_resnet, y_pred_resnet = evaluate_model(resnet_model, x_test, y_test, class_names, "ResNet")

    # ========== 6. 模型对比 ==========
    print("\n【步骤6】模型性能对比")
    print("=" * 50)
    print(f"{'模型':<20} {'准确率':<12} {'损失':<12}")
    print("-" * 50)
    print(f"{'优化版CNN':<20} {acc_cnn:.4f}       {loss_cnn:.4f}")
    print(f"{'VGGNet':<20} {acc_vgg:.4f}       {loss_vgg:.4f}")
    print(f"{'ResNet':<20} {acc_resnet:.4f}       {loss_resnet:.4f}")

    # 绘制对比曲线
    plot_comparison([history_cnn, history_vgg, history_resnet],
                    ["优化版CNN", "VGGNet", "ResNet"])

    # ========== 7. 混淆矩阵 ==========
    print("\n【步骤7】混淆矩阵分析")
    print("-" * 40)

    plot_confusion_matrix(y_test, y_pred_vgg, class_names, "VGGNet混淆矩阵")
    plot_confusion_matrix(y_test, y_pred_resnet, class_names, "ResNet混淆矩阵")

    # ========== 8. 预测样本展示 ==========
    print("\n【步骤8】预测样本展示")
    print("-" * 40)

    plot_sample_predictions(vgg_model, x_test, y_test, class_names)

    # ========== 9. 错误分析 ==========
    print("\n【步骤9】错误分析")
    print("-" * 40)

    errors_vgg = np.where(y_pred_vgg != y_test)[0]
    errors_resnet = np.where(y_pred_resnet != y_test)[0]

    print(f"VGGNet 错误分类: {len(errors_vgg)}/{len(y_test)} ({len(errors_vgg) / len(y_test) * 100:.2f}%)")
    print(f"ResNet 错误分类: {len(errors_resnet)}/{len(y_test)} ({len(errors_resnet) / len(y_test) * 100:.2f}%)")

    # 显示错误样本
    if len(errors_vgg) > 0:
        n_show = min(9, len(errors_vgg))
        fig, axes = plt.subplots(3, 3, figsize=(9, 9))
        axes = axes.ravel()

        for i in range(n_show):
            idx = errors_vgg[i]
            if x_test[idx].shape[-1] == 1:
                axes[i].imshow(x_test[idx].squeeze(), cmap='gray')
            else:
                axes[i].imshow(x_test[idx])
            axes[i].set_title(f'真实: {class_names[y_test[idx]]}\n预测: {class_names[y_pred_vgg[idx]]}')
            axes[i].axis('off')

        for i in range(n_show, 9):
            axes[i].axis('off')

        plt.suptitle('VGGNet错误分类样本', fontsize=14)
        plt.tight_layout()
        plt.show()

    # ========== 10. 保存最佳模型 ==========
    print("\n【步骤10】保存最佳模型")
    print("-" * 40)

    results = [("优化版CNN", acc_cnn), ("VGGNet", acc_vgg), ("ResNet", acc_resnet)]
    best_name, best_acc = max(results, key=lambda x: x[1])

    if best_name == "优化版CNN":
        best_model = cnn_model
    elif best_name == "VGGNet":
        best_model = vgg_model
    else:
        best_model = resnet_model

    best_model.save('best_gesture_model.h5')
    print(f"最佳模型: {best_name} (准确率: {best_acc:.4f})")
    print("模型已保存为 'best_gesture_model.h5'")

    # ========== 实验总结 ==========
    print("\n" + "=" * 70)
    print("实验完成！")
    print("=" * 70)
    print("\n实验总结:")
    print("1. 成功实现了手势识别CNN模型")
    print("2. 对比了优化CNN、VGGNet、ResNet三种模型")
    print(f"3. 最佳模型: {best_name}, 准确率: {best_acc:.4f}")
    print("4. VGGNet结构规整，适合作为baseline")
    print("5. ResNet通过残差连接解决了梯度问题")
    print("\n模型已保存，可使用以下代码加载:")
    print("model = tf.keras.models.load_model('best_gesture_model.h5')")

    return best_model, results


# 模型加载预测函数
def predict_gesture(model, image_path, class_names, img_size=(64, 64)):
    """对单张图片进行预测"""
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize(img_size)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)
    pred_class = np.argmax(predictions[0])
    confidence = predictions[0][pred_class]

    print(f"预测手势: {class_names[pred_class]}")
    print(f"置信度: {confidence:.4f}")

    return pred_class, confidence


# 运行主程序
if __name__ == "__main__":
    best_model, results = main()