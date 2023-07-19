# 霍夫曼编码

## 问题定义

有一种语言，它由四个字母组成 {a, b, c, d}, 我们要把它编码成电报发送出去(电报只有 2 种字符，即二进制{0, 1}),
要怎么编码才最短，才能保证传输效率尽可能高。

一种很直观的想法是，定义 {a=00, b=01, c=10, d=11} ，不过并不能保证这种编码转译出来的编码最短。

霍夫曼编码算法，正式为了解决这个问题。

## 算法步骤

霍夫曼算法需要先统计所有字符出现的概率。对于一种语言来说，这个概率一般是固定的，例如汉语中，`的` 字出现很多，而`霍`出现的比较少。

统计各个字母出现概率后，接下来思路就是针对出现概率高的字符分配比较短的编码，出现概率低的字符分配长编码。

假设刚才 {a,b,c,d} 出现概率分别为 {0.5, 0.25, 0.125, 0.125}. 我们构造下面的初始节点

```{mermaid}
graph TD
    a(a 0.5)
    b(b 0.25)
    c(c 0.125)
    d(d 0.125)
```

霍夫曼编码就是每次取概率最小的两个节点，合并为一个大节点，
循环往复，直到最后只剩下一个节点。

第一步，合并概率最低的 c/d 节点，形成一个新节点, 新节点的概率等于 c/d 的概率相加(0.25)。

```{mermaid}
graph BT
    a(a 0.5)
    b(b 0.25)
    c(c 0.125):::dimmed
    d(d 0.125):::dimmed

    cd(cd 0.25)
    classDef dimmed fill:#bbb

    c --> cd
    d --> cd
```

第二步，合并概率最低的 b/cd 节点

```{mermaid}
graph BT
    a(a 0.5)
    b(b 0.25):::dimmed
    c(c 0.125):::dimmed
    d(d 0.125):::dimmed

    cd(cd 0.25):::dimmed
    bcd(bcd 0.5)
    classDef dimmed fill:#bbb

    c --> cd
    d --> cd
    b --> bcd
    cd --> bcd
```

第三步，现在只剩下两个节点了，把他们合并成一个。

```{mermaid}
graph BT
    a(a 0.5):::dimmed
    b(b 0.25):::dimmed
    c(c 0.125):::dimmed
    d(d 0.125):::dimmed

    cd(cd 0.25):::dimmed
    bcd(bcd 0.25):::dimmed
    abcd(bcd 1.0)
    classDef dimmed fill:#bbb

    c --> cd
    d --> cd
    b --> bcd
    cd --> bcd
    a --> abcd
    bcd --> abcd
```

得到这棵树后，定义树的左节点是 0，右节点是 1. 就能得到霍夫曼编码

```{mermaid}
graph BT
    a(a 0):::dimmed
    b(b 0):::dimmed
    c(c 0):::dimmed
    d(d 1):::dimmed

    cd(cd 1):::dimmed
    bcd(bcd 1):::dimmed
    abcd(root)
    classDef dimmed fill:#bbb

    c --> cd
    d --> cd
    b --> bcd
    cd --> bcd
    a --> abcd
    bcd --> abcd
```

所以按照树从上到下的路径，得到:

```text
a = 0
b = 10
c = 110
d = 111
```

我们可以计算一下这种语言平均编码长度，即每个字符概率乘以他们的编码长度 $\sum(p_i*len(C_i))$ :

```text
0.5*1 + 0.25*2 + 0.125 * 3 + 0.125 * 3
= 0.5 + 0.5 + 0.375 + 0.375
= 1.75
```

而我们最初提出的 {a=00, b=01, c=10, d=11} 平均需要 2 字符，霍夫曼编码平均需要 1.75 字符，结果是要好很多的。
