# mosoo managed agent for Dify

把一个已发布的 [mosoo](https://mosoo.ai) 智能体作为原生工具用于 Dify Agent、Chatflow 和 Workflow。mosoo 是 harness 中立的托管智能体运行时：Dify 只提交任务，模型、工具、沙箱、记忆和执行生命周期由 mosoo 管理。

`Dify -> mosoo Thread API -> 已发布 Agent -> 已配置 runtime + model`

## 能力

- 一个 **mosoo managed agent** 工具，支持新建 Thread、续聊和只等待三种模式。
- 返回标准最终答复，以及供 Workflow 分支使用的 `thread_id`、`run_id`、`status`、`error`。
- 长任务超时不会丢失：保存返回的 `thread_id`，再次调用并留空任务即可继续等待。
- API Token 只发送到固定地址 `https://cloud.mosoo.ai/api/v1`，不接受自定义主机。

## 配置步骤

1. 登录 [mosoo Cloud](https://cloud.mosoo.ai)，添加模型供应商密钥，创建并测试 Agent，然后发布。到 Agent 列表或设置中复制 26 位 Agent ID。
2. 打开 **Settings -> Access tokens**，填写标签并点击 **Create**，复制只显示一次的 `mst_...` Token。

![创建 mosoo API Token](../_assets/mosoo-api-token.png)

3. 在 Dify Marketplace 安装 **mosoo managed agent**。插件发布前，可在 **Plugins -> Install from local package** 上传构建好的 `mosoo.difypkg`。
4. 填入 mosoo API Token 和已发布 Agent ID。凭据校验只做只读请求。

![在 Dify 配置 mosoo](../_assets/dify-provider-config.jpg)

5. 在 Dify Agent 的 Tools 中添加 **mosoo managed agent**；或在 Chatflow/Workflow 添加 **Tool** 节点并选择它。

![在 Dify Workflow 使用 mosoo](../_assets/dify-workflow-tool.jpg)

## 用法

| 目标        | `prompt` | `thread_id` |
| ----------- | -------- | ----------- |
| 新建任务    | 必填     | 留空        |
| 继续 Thread | 必填     | 上次返回值  |
| 继续等待    | 留空     | 上次返回值  |

`timeout_seconds` 默认 120 秒（范围 10-240）。插件把 Dify runtime user 映射到 mosoo `userId`，并拒绝继续其他 Dify 用户的 Thread。返回 `waiting_input` 时，请先在 mosoo 处理权限或输入，再只带 `thread_id` 调用。

## 支持的 runtime

mosoo 是托管智能体 runtime，不是 Dify 模型供应商。插件只运行已发布的 Agent；runtime 与模型在 mosoo 中配置。当前公开 runtime 为：

- **Claude Agent SDK**：支持 Anthropic Claude 模型。
- **OpenAI Runtime**：支持 OpenAI GPT 模型，以及实现 Responses API 的自定义 OpenAI-compatible 端点。
- **OpenCode**：支持 Anthropic、OpenAI、DeepSeek、Gemini、Qwen、Kimi、Zhipu、MiniMax、OpenCode Zen 和自定义 OpenAI-compatible 模型。

实际可用模型取决于 mosoo 中已配置的供应商密钥和当前 [mosoo runtime catalog](https://github.com/langgenius/mosoo/blob/main/pkgs/runtime-catalog/catalog/runtime-catalog.jsonc)。

## 安全、隐私与源码

任务会发送给 mosoo；已配置 Agent 可能调用远程模型、工具、MCP、网络或在沙箱内执行命令。发布 Agent 前请检查这些能力。插件自身没有持久化存储或分析埋点，详见 [PRIVACY.md](../PRIVACY.md)。

源码：[mosoo-ai/dify-plugin-mosoo](https://github.com/mosoo-ai/dify-plugin-mosoo) · 文档：[mosoo.ai/docs](https://mosoo.ai/docs/) · 支持：[GitHub Issues](https://github.com/mosoo-ai/dify-plugin-mosoo/issues) · 联系：[cyefan2@gmail.com](mailto:cyefan2@gmail.com)
