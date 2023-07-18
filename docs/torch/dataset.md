# Dataset

要自定义 torch 的数据集，会涉及到两个模块:

- `Dataset`: 自己实现的类, 用于返回一条一条的数据
- `DataLoader`: torch 提供的数据加载器，传入 Dataset，按照 batch 返回数据，并且提供一些(乱序、多进程等)加载方法可供组合。

也就是，需要实现 Dataset 说明数据如何读取，然后传给 DataLoader 去读取数据

## 两种 Dataset 接口

Dataset 有两种接口：

1. map-style: 继承 `torch.utils.data.Dataset`
2. iterable-style. 继承 `torch.utils.data.IterableDataset`

Dataset 适合用于可以一次性加载到内存的小数据，IterableDataset 适合用于无法一次性加载到内存的大数据。
Dataset 用起来简单一些，限制也比较少。

### torch.utils.data.Dataset

继承 Dataset 需要实现 `__getitem__`/`__len__` 方法.

这个方法是 python 中字典取数的方法，如 `some_dict['key']` 实际等价于 `some_dict.__getitem__('key')`。所以这种风格称为 map-style 数据集。

DataLoader 如果接收到了一个 map-style 数据集，通过 `n = len(dataset)` 获取数据集中的元素个数，然后把 $[0, n)$ 作为参数依次调用 `__getitem__` 进行取数。
如果需要 shuffle ， DataLoader 也会打乱 key 的顺序，再调用 `__getitem__`，因此特别适用于内存数据，如果是数据库或者磁盘数据的话，乱序读取性能比较低。

### Dataset 案例

#### 简单的数据集

一个简单的案例，我们有一些随机数

```python
from torch.utils.data import Dataset

class SimpleDataset(Dataset):
    def __init__(self):
        # 拥有四个数据的数据集
        self._data = [2, 3, 5, 7, 11]

    def __len__(self):
        """返回数据集长度"""
        return len(self._data)

    def __getitem__(self, index: int):
        """获取数据集某一个下标的元素"""
        return self._data[index]
```

这就是一个最简单的案例。

#### 更真实的案例

如果希望有一个更真实的案例，例如有一批图片作为训练数据存放在内存，只要将上面的例子稍微改造一下即可实现.

```python
class ImageDataset(Dataset):
    def __init__(self):
        self._images = [ ]
        # 把所有图片存放到内存
        for img_path in glob.glob(".../*.jpg"):
            self._images.append(read_image(img_path))

    def __len__(self):
        return len(self._images)

    def __getitem__(self, index: int):
        return self._images[index]
```

再假如我们的图片很多，无法一次性加载到内存，只能运行时临时从磁盘、数据库读取。可以在类中只保存文件路径。

```python
from torch.utils.data import Dataset

class ImageDataset(Dataset):
    def __init__(self):
        # 只存放所有文件路径
        self._img_names = [ ]

    def __len__(self):
        return len(self._img_names)

    def __getitem__(self, index: int):
        img_path = self._img_names[index]
        return read_image(img_path)
```

不过，实时从磁盘读取比从内存读取慢几个数量级。

### 使用 Dataset

#### python 代码中使用

通过 python 代码可以测试刚才定义的 Dataset:

```python
ds = SimpleDataset()

ds_size = len(ds) # 5
img_one = ds[0] # 2
img_two = ds[1] # 3

for index in range(len(ds)):
    item = ds[index]
    print(item)
# 输出: 2,3,5,7,11
```

或者：

```python
for index in range(len(ds)):
    item = ds[index]
    # 使用这条数据进行训练
    train_batch(item)
```

不过，一般不会通过这种方式, 而是通过 `DataLoader`。在最简单的情况下，DataLoader 的内部实现其实就是上面的 for 循环: 挨个取出里面的元素, 丢给外面进行训练。

所以，我们为什么非要 DataLoader 呢?
因为 Dataloader 还提供了一大堆简单

## DataLoader

使用 DataLoader 加载数据集:

```python
ds = SimpleDataset()
data_loader = DataLoader(ds)

for item in data_loader:
    print(item)
# 输出:
# tensor([2])
# tensor([3])
# tensor([5])
# tensor([7])
# tensor([11])
```

嗯... 似乎和我们直接 python 代码迭代 Dataset 没什么区别?

其实还是有点区别的，它帮我们把 item 转换成了 tensor... 好像还是没区别。

这是因为我们还没有调教好，DataLoader 提供了大量可复用功能: 分 batch，随机采样，多进程加载等, 下面一一介绍。

### batch_size

```python
for item in DataLoader(ds, batch_size=2):
    print(item)
# 输出:
# tensor([1, 2])
# tensor([3, 4])
# tensor([5])
```

设置 batch_size=2 后，每次输出 2 个

### drop_last

设置 batch_size 后，由于最后一个 batch 可能数量不足 2 个，如果有特殊需求要舍弃这部分不足一个 batch 的数据，可以设置 drop_last

```python
for item in DataLoader(ds, batch_size=2, drop_last=True):
    print(item)
# 输出:
# tensor([1, 2])
# tensor([3, 4])
```

### shuffle

乱序加载

```python
for item in DataLoader(ds, batch_size=2, shuffle=True):
    print(item)
# 输出:
# tensor([2, 4])
# tensor([5, 3])
# tensor([1])
```

### Sampler

### 多进程加载

### torch.utils.data.IterableDataset

继承 IterableDataset 需要实现 `__iter__` 方法，这个方法是 python 迭代数组的方法。例如 `for item in data_list`，会运行一次 `data_list.__iter__()` 得到一个迭代器，然后每次循环通过迭代器获取 item 。
