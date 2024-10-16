# OLLVM

## 常用参数

-mllvm -sub: 指令替代
-mllvm -bcf: 控制流程伪造
-mllvm -fla: 控制流平坦化

-mllvm -perBCF=20: 对所有函数都混淆的概率是20%，默认100%
-mllvm -boguscf-loop=3: 对函数做3次混淆，默认1次
-mllvm -boguscf-prob=40: 代码块被混淆的概率是40%，默认30%