# Tensor

1. 向量可以进行加减乘除，并且一般有两种形式: `c = a.add(b)` `c = torch.add(a, b)`， 它们一般并不修改原始向量，而是运算后生成新向量返回。
2. 向量的数学运算提供原地运算方法，一般方法名以下划线结尾, 如 `a.add_(b)`, 这些运算会直接在原始向量上修改，一般会修改原始向量的方法都以下划线结尾。
3. Tensor.to("gpu") 可以将向量转移到 gpu. 同样的 to 函数，也可以进行类型转换: Tensor.to(torch.float32)
4. model.eval() 函数，会递归设置所有层的 `training` 属性为 False
5. torch.no_grad() 会将模型的自动求梯度的功能去除，一般用于预测流程
6. Tensor.detatch() 会返回一个不带梯度的 Tensor。、
7. 指定 `requires_grad=True`, 如 `torch.tensor(..., requires_grad=True)`, 可以使向量具有求梯度的功能。
8. 使用 `torch.autograd.profiler.profile` 可以查看反向传播的耗时
9. 使用 `torch.profiler.profile` 查看 forward 耗时
10. `torch.autograd.functional.jacobian` `torch.autograd.functional.vjp`
11. 模型解释 [captum](https://captum.ai/)
12. 混合精度 [apex](https://github.com/NVIDIA/apex)

## 操作

### T

二维矩阵转置的视图，例如 t 是二维矩阵， `b = t.T`, 则 $b_{i,j} = t_{j,i}$

:::warning

不要使用在非二维矩阵上，对于这种场景，使用 `mT` 或者 `permute` 替代

:::

### H

针对二维矩阵，返回转置后的共轭矩阵的视图，等价于 `t.transpose(0, 1).conj()`

```python
t = torch.tensor([[1, 2+2j], [3, 4+4j]])
print(t)
#[[1.0, 2.0+2.0j],
# [3.0, 4.0+4.0j]]

print(t.transpose(0, 1))
#[[1.0     , 3.0],
# [2.0+2.0j, 4.0+4.0j]]

print(t.transpose(0, 1).conj())
#[[1.0     , 3.0],
# [2.0-2.0j, 4.0-4.0j]]

print(t.H)
#[[1.0     , 3.0],
# [2.0-2.0j, 4.0-4.0j]]
```

### mT

对矩阵的最后两维进行转置后的视图，例如对于三维矩阵 t: `b = t.mT`,
表示 $b_{i,j,k} = t_{i,k,j}$ ,等价于 `t.transpose(-2, -1)`

### mH

等价于 `t.transpose(-2, -1).conj()`, 可用于高于二维的矩阵，
将最后两维转职后的共轭矩阵的试图。
