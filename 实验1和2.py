import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import train_test_split
from matplotlib.colors import ListedColormap

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 1. 数据导入及可视化
X, y = datasets.make_moons(n_samples=1000, noise=0.2, random_state=100)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print(X.shape, y.shape)

def make_plot(X, y, plot_name):
    plt.figure(figsize=(12, 8))
    plt.title(plot_name, fontsize=30)
    plt.scatter(X[y==0, 0], X[y==0, 1], label='类别0')
    plt.scatter(X[y==1, 0], X[y==1, 1], label='类别1')
    plt.legend()
    plt.show()

make_plot(X, y, "双月数据分类可视化")

# 2. 网络层实现
class Layer:
    def __init__(self, n_input, n_output, activation=None, weights=None, bias=None):
        self.weights = weights if weights is not None else np.random.randn(n_input, n_output) * np.sqrt(1 / n_output)
        self.bias = bias if bias is not None else np.random.rand(n_output) * 0.1
        self.activation = activation
        self.activation_output = None
        self.error = None
        self.delta = None

    def activate(self, X):
        r = np.dot(X, self.weights) + self.bias
        self.activation_output = self._apply_activation(r)
        return self.activation_output

    def _apply_activation(self, r):
        if self.activation is None:
            return r
        elif self.activation == 'relu':
            return np.maximum(r, 0)
        elif self.activation == 'tanh':
            return np.tanh(r)
        elif self.activation == 'sigmoid':
            return 1 / (1 + np.exp(-r))
        return r

    def apply_activation_derivative(self, r):
        # 计算激活函数的导数
        if self.activation is None:
            return np.ones_like(r)
        elif self.activation == 'sigmoid':
            sig = 1 / (1 + np.exp(-r))
            return sig * (1 - sig)
        elif self.activation == 'tanh':
            return 1 - np.tanh(r) ** 2
        elif self.activation == 'relu':
            return (r > 0).astype(float)
        else:
            return np.ones_like(r)

# 3. 网络模型
class NeuralNetwork:
    def __init__(self):
        self._layers = []

    def add_layer(self, layer):
        self._layers.append(layer)

    def feed_forward(self, X):
        for layer in self._layers:
            X = layer.activate(X)
        return X

    def backpropagation(self, X, y, learning_rate):
        # 前向传播
        self.feed_forward(X)
        # 反向传播
        num_layers = len(self._layers)
        # 输出层delta计算（使用均方误差 + sigmoid导数）
        output_layer = self._layers[-1]
        output = output_layer.activation_output
        # 将y转为one-hot编码（二分类）
        y_onehot = np.zeros_like(output)
        y_onehot[0, y] = 1
        # 误差 = (output - y) * sigmoid导数
        delta = (output - y_onehot) * output_layer.apply_activation_derivative(output)
        output_layer.delta = delta
        # 更新输出层权重和偏置
        prev_output = self._layers[-2].activation_output if num_layers > 1 else X
        output_layer.weights -= learning_rate * np.dot(prev_output.T, delta)
        # 确保bias形状一致
        bias_update = learning_rate * np.sum(delta, axis=0)
        output_layer.bias -= bias_update.reshape(output_layer.bias.shape)

        # 从后向前更新隐藏层
        for i in range(num_layers - 2, -1, -1):
            layer = self._layers[i]
            next_layer = self._layers[i + 1]
            # 当前层的delta = (下一层权重 * 下一层delta) * 当前层激活函数导数
            delta = np.dot(next_layer.delta, next_layer.weights.T) * layer.apply_activation_derivative(layer.activation_output)
            layer.delta = delta
            # 更新当前层权重和偏置
            prev_output = self._layers[i - 1].activation_output if i > 0 else X
            layer.weights -= learning_rate * np.dot(prev_output.T, delta)
            # 确保bias形状一致
            bias_update = learning_rate * np.sum(delta, axis=0)
            layer.bias -= bias_update.reshape(layer.bias.shape)

    def train(self, X_train, X_test, y_train, y_test, learning_rate, max_epochs):
        train_losses = []
        test_accuracies = []
        for epoch in range(max_epochs):
            # 每个epoch训练所有样本
            for i in range(len(X_train)):
                x_sample = X_train[i].reshape(1, -1)
                y_sample = y_train[i]
                self.backpropagation(x_sample, y_sample, learning_rate)

            # 计算训练集均方误差
            y_train_pred_probs = self.feed_forward(X_train)
            y_train_pred = np.argmax(y_train_pred_probs, axis=1)
            train_loss = np.mean((y_train_pred - y_train) ** 2)
            train_losses.append(train_loss)

            # 计算测试集准确率
            y_test_pred = self.predict(X_test)
            accuracy = self.accuracy(y_test_pred, y_test)
            test_accuracies.append(accuracy)

            if epoch % 10 == 0:
                print(f"训练轮次 {epoch}, 损失: {train_loss:.4f}, 准确率: {accuracy:.4f}")
        return train_losses, test_accuracies

    def accuracy(self, y_predict, y_test):
        return np.sum(y_predict == y_test) / len(y_test)

    def predict(self, X_predict):
        y_probs = self.feed_forward(X_predict)
        y_pred = np.argmax(y_probs, axis=1)
        return y_pred

# 4. 网络训练
nn = NeuralNetwork()
nn.add_layer(Layer(2, 25, activation='sigmoid'))   # 隐藏层1
nn.add_layer(Layer(25, 50, activation='sigmoid'))  # 隐藏层2
nn.add_layer(Layer(50, 25, activation='sigmoid'))  # 隐藏层3
nn.add_layer(Layer(25, 2, activation='sigmoid'))   # 输出层（二分类）

# 训练网络
learning_rate = 0.1
max_epochs = 100
print("开始训练...")
train_losses, test_accuracies = nn.train(X_train, X_test, y_train, y_test, learning_rate, max_epochs)

# 预测与精度计算
y_predict = nn.predict(X_test)
accuracy = nn.accuracy(y_predict, y_test)
print(f"\n最终测试准确率: {accuracy:.4f}")

# 5. 决策边界可视化（中文标题）
def plot_decision_boundary(model, axis):
    x0, x1 = np.meshgrid(
        np.linspace(axis[0], axis[1], int((axis[1] - axis[0]) * 100)).reshape(1, -1),
        np.linspace(axis[2], axis[3], int((axis[3] - axis[2]) * 100)).reshape(-1, 1)
    )
    X_new = np.c_[x0.ravel(), x1.ravel()]
    y_predic = model.predict(X_new)
    zz = y_predic.reshape(x0.shape)
    custom_cmap = ListedColormap(['#EF9A9A', '#FFF590', '#90CAF9'])
    plt.contourf(x0, x1, zz, cmap=custom_cmap, alpha=0.8)
    plt.contour(x0, x1, zz, colors='black', linewidths=0.5, alpha=0.3)

plt.figure(figsize=(12, 8))
plot_decision_boundary(nn, [-2, 2.5, -1, 2])
plt.scatter(X[y==0, 0], X[y==0, 1], label='类别0', alpha=0.7)
plt.scatter(X[y==1, 0], X[y==1, 1], label='类别1', alpha=0.7)
plt.title("神经网络决策边界", fontsize=16)  # 中文标题
plt.xlabel("特征1", fontsize=12)  # 中文标签
plt.ylabel("特征2", fontsize=12)  # 中文标签
plt.legend()
plt.show()

# 绘制训练曲线（中文标题）
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(train_losses)
plt.title('训练损失曲线', fontsize=14)  # 中文标题
plt.xlabel('训练轮次', fontsize=12)  # 中文标签
plt.ylabel('均方误差损失', fontsize=12)  # 中文标签
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(test_accuracies, color='orange')
plt.title('测试准确率曲线', fontsize=14)  # 中文标题
plt.xlabel('训练轮次', fontsize=12)  # 中文标签
plt.ylabel('准确率', fontsize=12)  # 中文标签
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 打印统计信息
print(f"\n训练统计:")
print(f"初始损失: {train_losses[0]:.4f}")
print(f"最终损失: {train_losses[-1]:.4f}")
print(f"最佳准确率: {max(test_accuracies):.4f}")
print(f"最终准确率: {test_accuracies[-1]:.4f}")