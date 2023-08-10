# 开发对 Llama 原理的理解

## 基础知识

### 全连接

深层全连接网络具备拟合任意函数的能力。

困难: 深层全连接网络存在梯度弥散问题，无法训练

### 解决全连接无法训练的问题

1. 使用一些 trick, 如残差
2. 尝试不同的激活函数
3. 设计专用的网络如 cnn/lstm/bert 等，使其更容易学习到某些特征。llama 使用的 attention 也在此列。

### 模型设计与传统算法设计的区别

设计模型时，给模型提供数据以及一种可能性，而非直接的逻辑

例如，提供模型必要的特征，而不必告诉模型特征之间的关系，让它自己学习如何组合。

再例如，设计网络时，将前后三个文字拼接起来(CNN)。即设计专用网络

### 迁移学习

深度学习模型训练好后，有人发现，模型前半部分固定，把后半部分砍掉，改成其他网络，然后只训练后半部分，能够很好的完成任务。

原因是，网络的中间层已经学习到了数据知识的表示。

这意味着:

1. 可复用性。

   如果已经存在一个训练好的模型，取出前半段，利用其学习到数据中的知识表示，那么后期再接上其他浅层网络微调，可以直接复用.

   而且浅层网络极易训练，参数很少，大部分参数在前半段，意味着花费极短时间就能够达到同等大模型的效果。

2. 无监督

   由于前半段模型并不需要了解业务，而是集中在了解数据“自身”。

   因此不需要数据标注，可以完全无监督学习，这也为海量数据训练提供了可能

## Llama

![llama 网络结构](/_static/torch/llama/llama.drawio.svg)

## Self-Attention

上图中最后一部分 **Attention** 就是 Self-Attention，llama 正是通过 Self-Attention 了解数据自身。

![q/k matrix](/_static/torch/llama/q_k.drawio.svg)

假设输入是 $X$ ，Query/Key/Value 三个 Matrix 的来源:

- Query: $Q = W_q * X$
- Key: $K = W_k * X$
- Value: $V = W_v * X$

从实现上来看， Query/Key 是一样的，命名不同是从 Transformer 继承过来的概念。
直观一点理解可以看作一句话中，每个字的向量互相进行两两相乘(点乘)得到的矩阵(数学意义就是计算 cos 相似度)。
可以看出这一步的复杂度是 $O(n^2)$ 如果是 100 字的文本，矩阵大小是 `100*100=10000` 元素, 如果是 10000 字的文本，结果就是 1 亿个元素，估计就计算不出来了。

K/Q 在相乘之前，还要进行一次旋转（即乘以 $e^{im\theta}$ ）, 例如对于 m、n 两个位置的字符:

$Q_{m} = W_q X e^{im\theta}$

$K_{n} = W_k X e^{in\theta}$

$G_{m,n} = Q_{m} \cdot K_{n}$

这样看起来可能觉得平平无奇，实际上函数 G 是一个形式为 $g(X_m, X_n, m-n)$ 的函数，里面隐藏了一个 (m-n) 参数，
因此它除了能够关注到每个字符之间的两两关系外，字符之间的位置相对位置也会被关注到，这也是 Attention 和传统 RNN 网络的区别。

## QKV 的推导

下面推导为什么 **函数 $G=K^TQ$ 是一个形式为 $g(X_m, X_n, m-n)$ 的函数**。
不过不关注原理也不影响。

以第 6 个字 "他"和第 0 个字"小"为例，它们存在指代关系， $Q_6 \cdot K_0$ (cos 相似度)结果应该比较大(不过大小不是现在要关注的事情):

### 基础: 复数矩阵运算

下面是为了说明：$M*e^{i\theta} = R_{\theta}M$

根据欧拉公式:

$$
\begin{aligned}
e^{i\theta} &= cos(\theta) + i*sin(\theta) \\
e^{im\theta} &= cos(m\theta) + i*sin(m\theta)
\end{aligned}
$$

所以，对于一个拥有两个元素的列向量 $M = [m_1, m_2]$,
将它转换到复数域: $M = m_1 + i * m_2$ ,
对它施加乘法操作，就得到了:

$$
\begin{aligned}

M e^{i\theta} &= (m_1 + i * m_2)(cos(\theta) + i*sin(\theta)) \\
   &= m_1cos(\theta) - m_2  sin(\theta) + i(m_1sin(\theta) + m_2 cos(\theta)) \\
   & = \left\lbrack \begin{array}{} cos(\theta)&-sin(\theta) \\ sin(\theta)&cos(\theta) \end{array}\right\rbrack
   \left\lbrack \begin{array}{} m_1 \\ m_2 \end{array}\right\rbrack

\end{aligned}
$$

$\left\lbrack \begin{array}{} cos(\theta)&-sin(\theta) \\ sin(\theta)&cos(\theta) \end{array}\right\rbrack$ 这个矩阵是固定的，下面记录为 $R_{\theta}$

最后我们得到了： $M*e^{i\theta} = R_{\theta}M$

### 推导过程

在推导之前，可以看出显然 $G = Q \cdot K$ 是一个 $g(x_m, x_n)$ 形式的函数，因为 $x_m, x_n$ 就是直接输入。

接下来验证它也是一个形如 $g(x_m, x_n, m-n)$ 的函数。

$$
\begin{aligned}
G_{m,n}
   &= Q_m^T * K_n \\
   & = (W_q X_m e^{im\theta})^T  (W_k X_n e^{in\theta}) \\
   & = (R_{m\theta} (W_q X_m))^T  (R_{n\theta} (W_k X_n) ) \\
   & = ((W_q X_m)^T  R_{m\theta} ^T)  (R_{n\theta} (W_k X_n) ) \\
   & = (W_q X_m)^T  R_{m\theta} ^T  R_{n\theta} (W_k X_n) \\
\end{aligned}
$$

嗯。。。好像有点复杂了，现在把注意力集中在中间的 $R_{m\theta} ^T  R_{n\theta}$

$$
\begin{aligned}
R_{m\theta} ^T  R_{n\theta} & = \left\lbrack \begin{array}{}
      cos(m\theta)&-sin(m\theta) \\
      sin(m\theta)&cos(m\theta)
   \end{array}\right\rbrack ^T
   \left\lbrack

   \begin{array}{}
      cos(n\theta)&-sin(n\theta) \\
      sin(n\theta)&cos(n\theta)
   \end{array}\right\rbrack \\

   & = \left\lbrack \begin{array}{}
      cos(m\theta)&sin(m\theta) \\
      -sin(m\theta)&cos(m\theta)
   \end{array}\right\rbrack
   \left\lbrack

   \begin{array}{}
      cos(n\theta)&-sin(n\theta) \\
      sin(n\theta)&cos(n\theta)
   \end{array}\right\rbrack \\

   & = \left\lbrack \begin{array}{}
      cos(m\theta)cos(n\theta)+sin(m\theta)sin(n\theta)&-cos(m\theta)sin(n\theta)+sin(m\theta)cos(n\theta) \\
      -sin(m\theta)cos(n\theta)+cos(m\theta)sin(n\theta)&sin(m\theta)sin(n\theta)+cos(m\theta)cos(n\theta)
   \end{array}\right\rbrack \\

   & = \left\lbrack \begin{array}{}
      cos(m\theta - n\theta)&sin(m\theta - n\theta) \\
      -sin(m\theta - n\theta)&cos(m\theta - n\theta)
   \end{array}\right\rbrack \\

   & = \left\lbrack \begin{array}{}
      cos((m- n)\theta)&sin((m - n)\theta) \\
      -sin((m - n)\theta)&cos((m - n)\theta)
   \end{array}\right\rbrack \\

   & = R_{(m-n)\theta}

\end{aligned}
$$

以上只涉及到了基础的矩阵乘法和三角函数运算。接上最初的推导，
可以看出 $Q \cdot K$ 是一个形如 $g(x_m, x_n, m-n)$ 的函数:

$$
\begin{aligned}
G_{m,n}
   & = (W_q X_m)^T  R_{m\theta} ^T  R_{n\theta} (W_k X_n) \\

   & = (W_q X_m)^T R_{(m-n)\theta} ^T (W_k X_n)
\end{aligned}
$$

现在剩下最后一个问题，以上推导都是假定 M 向量拥有两个元素: $M = [m_1, m_2]$.
如果 M 是一个更高维向量呢？处理方法就是把他们拆分为两个一组，分别进行上面的运算。
比如 $M = [m_1, m_2, m_3, m_4]$ 拆分为两组 $[[m_1, m_2],[ m_3, m_4]]$

如果是 M 维度是奇数，最后一个看作他们复数部分是 0，比如 $M = [m_1, m_2, m_3]$ 就变成 $[[m_1, m_2],[ m_3, 0 ]]$ 即最后一组是 $m_3 + i0$

## MLP

先将数据升维，好提取特征中的某些组成成分，然后再合并降维成原来的大小。

## ... ...
