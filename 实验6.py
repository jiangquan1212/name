# 1. 导入所需包
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam

# 忽略警告信息
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 2. 数据预处理与增强
train_datagen = ImageDataGenerator(
    rescale=1.0/255,          # 删除多余的路径参数
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

test_datagen = ImageDataGenerator(rescale=1.0/255)  # 使用 1.0/255 更清晰

# 使用原始字符串或双反斜杠（你的写法正确）
train_generator = train_datagen.flow_from_directory(
    r'D:\PythonProject2\data\images_base\train',  # r'' 原始字符串更简洁
    target_size=(150, 150),
    batch_size=32,
    class_mode='binary'
)

validation_generator = test_datagen.flow_from_directory(
    r'D:\PythonProject2\data\images_base\validation',
    target_size=(150, 150),
    batch_size=32,
    class_mode='binary'
)

# 打印实际 batch 数量
print(f"训练集 batch 数: {len(train_generator)}")
print(f"验证集 batch 数: {len(validation_generator)}")

# 3. 加载ResNet50（不包含顶层FC层）
# 如果本地有权重文件，建议使用本地文件避免下载
base_model = ResNet50(
    weights='imagenet',  # 或使用本地文件路径
    include_top=False,
    input_shape=(150, 150, 3)
)

# 4. 添加自定义FC层
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
x = Dropout(0.5)(x)  # 添加 Dropout 防止过拟合
predictions = Dense(1, activation='sigmoid')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# 冻结ResNet50的所有层
for layer in base_model.layers:
    layer.trainable = False

# 打印模型结构
model.summary()

# 5. 编译与训练（修正参数）
model.compile(
    optimizer=Adam(learning_rate=0.0001),  # 使用 learning_rate
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# 使用实际的 batch 数，不要写固定值
history = model.fit(
    train_generator,
    steps_per_epoch=len(train_generator),  # 自动获取实际值
    epochs=10,
    validation_data=validation_generator,
    validation_steps=len(validation_generator)  # 自动获取实际值
)

# 6. 测试准确率
loss, acc = model.evaluate(
    validation_generator,
    steps=len(validation_generator)  # 使用实际值
)
print("测试集准确率：", acc)