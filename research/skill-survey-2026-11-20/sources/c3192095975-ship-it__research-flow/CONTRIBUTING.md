# Contributing

感谢参与 Research Flow。

## 提交前

1. 不硬编码个人用户名、绝对目录或固定机器上的 skill 清单；
2. 新能力必须通过能力槽表达，而不是直接写死 skill 名称；
3. 外部依赖必须明确标记可用性；
4. 不执行或修改其他 skill；
5. 更新相关的 reference 和 handoff schema；
6. 运行测试：

```bash
python3 -m unittest discover -s tests -v
```

## 修改发现规则

如果增加新的能力信号，请同时补充：

- `references/capability-model.md` 中的角色定义；
- `scripts/discover_skills.py` 中的关键词或结构逻辑；
- `tests/test_discover_skills.py` 中的测试；
- `CHANGELOG.md`。

## 安全

不要在 skill 中保存密码、API Key、Cookie、私密项目数据或本机绝对路径。发现脚本只能读取元数据，不能执行其他 skill 的脚本。
