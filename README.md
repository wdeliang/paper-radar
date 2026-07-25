# Paper Radar — AI × Education & Equity

自动追踪 45 本顶级期刊（Nature/Science系、PNAS系、心理学/认知科学顶刊、教育学顶刊）的新发表文章，
用 DeepSeek-v4-pro 判断每篇是否与 **AI+教育 / 教育公平** 直接相关、或有**可迁移的研究启发**，
自动汇集到一个全英文网站上。部署一次后**全自动运行**：GitHub 每天定时抓取→筛选→更新网站，
你只需要定期打开网页看。

工作原理：
```
GitHub Actions 定时器（每天早上自动触发）
   → fetch_new.py   从 OpenAlex 抓取各期刊最近14天的新文章（自动去重）
   → screen_new.py  DeepSeek 逐篇判断：direct（直接相关）/ transferable（可迁移启发）/ 不相关
   → build_site.py  把纳入的文章累积进网站数据 papers.js
   → 自动提交到仓库 → GitHub Pages 网站自动更新
```

---

## 部署步骤（全程网页操作，不需要命令行）

### 第0步：准备两样东西

1. 一个 GitHub 账号（github.com 注册）。
2. 一个 DeepSeek API Key：打开 https://platform.deepseek.com → 注册 → 充值（充 10 元人民币够用几个月）→
   左侧 API keys → Create new API key → **复制保存好这串 sk- 开头的密钥**（只显示一次）。

### 第1步：创建仓库

1. GitHub 右上角 **＋** → **New repository**。
2. Repository name 填 `paper-radar`；选 **Public**；**不要**勾选 Add a README（我们自己有）。
3. 点 **Create repository**。

### 第2步：上传项目文件

1. 在新仓库页面，点 **uploading an existing file** 链接（或 Add file → Upload files）。
2. 把解压后文件夹里的这些文件**全部拖进去**：
   `config.py`、`fetch_new.py`、`screen_new.py`、`build_site.py`、
   `make_sample_data.py`、`requirements.txt`、`index.html`、`papers.js`、`README.md`
3. 下方 Commit changes 点绿色按钮提交。

### 第3步：创建自动化工作流文件（关键一步）

`.github` 开头的文件夹拖拽上传经常失败，所以我们手动创建：

1. 仓库页面点 **Add file** → **Create new file**。
2. 文件名一栏输入（注意斜杠，GitHub 会自动创建文件夹）：
   ```
   .github/workflows/update.yml
   ```
3. 打开你电脑上解压文件夹里的 `.github/workflows/update.yml`，**全选复制内容**，粘贴到网页编辑框。
4. 点 **Commit changes** 提交。

### 第4步：把 DeepSeek 密钥配置成 Secret（不要写进代码！）

1. 仓库页面 → **Settings** → 左侧 **Secrets and variables** → **Actions**。
2. 点 **New repository secret**。
3. Name 填（必须一字不差）：`DEEPSEEK_API_KEY`
4. Secret 填你的 sk- 开头密钥。
5. 点 **Add secret**。

> 为什么要这样：仓库是公开的，密钥写进代码等于把银行卡密码贴在门上。
> Secret 只有 GitHub Actions 运行时能读到，别人看不见。

### 第5步：开启网站（GitHub Pages）

1. **Settings** → 左侧 **Pages**。
2. Source 选 **Deploy from a branch**；Branch 选 `main`、目录 `/ (root)`；点 **Save**。
3. 等 1–3 分钟，刷新页面，顶部出现你的网址：
   `https://你的用户名.github.io/paper-radar/`
   现在打开会显示演示数据（因为 papers.js 还是示例）。

### 第6步：手动触发第一次运行

1. 仓库顶部点 **Actions** 标签页 →（如提示，点绿色按钮启用 workflows）。
2. 左侧点 **Update Paper Radar** → 右侧 **Run workflow** → 绿色 **Run workflow**。
3. 第一次会回填最近 30 天的文章，需要筛选一两千篇，**大约跑 20–60 分钟、花费 0.5–2 美元**。
   点进正在运行的任务可以实时看日志。
4. 跑完后（出现绿色对勾），等一两分钟刷新你的网站——真实数据上线。

### 第7步：完成！以后全自动

工作流每天北京时间早上 5:30 自动运行一次（增量只筛新文章，每天大约几十到两百篇、
成本几美分）。你什么都不用做，把网址收藏、分享给同学老师即可。

---

## 日常使用

- 网站顶部 **pulse 条**：每天纳入的文章数，点某一天只看那天的。
- **All / Direct / Transferable**：Direct = 直接是 AI+教育或教育公平的研究；
  Transferable = 其他领域但模型给出了一句话的迁移启发（写在 "Why it matters"）。
- 主题标签、期刊下拉、搜索框、排序（最新 / 被引 / 相关度）可叠加使用。
- 点标题 → 经 DOI 跳转出版社原文页。**Copy citation** 一键复制引用。

## 自定义

| 想改什么 | 改哪里 |
|---|---|
| 增删期刊 | `config.py` 的 JOURNALS（改完可本地跑 `python fetch_new.py --verify` 核对ISSN） |
| 改成每两天更新 | `.github/workflows/update.yml` 里 cron 换成 `"30 21 */2 * *"` |
| 筛选标准 | `screen_new.py` 顶部的 SYSTEM_PROMPT（比如加入你的具体研究关键词） |
| 省钱 | `config.py` 里模型换成 `deepseek-v4-flash` |
| 网站最多显示多少篇 | `config.py` 的 SITE_MAX_PAPERS |

改任何文件：在 GitHub 网页上点开文件 → 右上角铅笔 → 编辑 → Commit changes。下次运行自动生效。

## 本地运行（可选，用于调试）

```bash
pip install -r requirements.txt
set DEEPSEEK_API_KEY=sk-xxx        # Windows；Mac/Linux 用 export
python fetch_new.py
python screen_new.py --dry 20      # 先试筛20篇看看判断质量
python screen_new.py
python build_site.py
# 双击 index.html 查看
```

## 常见问题

- **Actions 运行失败？** Actions 页点进红叉的任务看哪一步报错：多数是 Secret 名字打错
  （必须是 `DEEPSEEK_API_KEY`）或 DeepSeek 余额不足。
- **定时任务会不会自己停？** GitHub 对 60 天无提交的仓库会暂停定时任务；本流水线每次运行
  都会提交心跳文件（data/last_run.json），所以不会触发这个问题。
- **某些文章没有摘要？** 部分出版社（主要是 Elsevier 系期刊）不向公共数据库提供摘要，
  模型会按标题判断并降低置信度。
- **想让同学也收到更新？** 直接把网址发给他们；或让他们在你的仓库点 Watch，有提交就有通知。
- **数据在哪里？** `data/archive.jsonl` 是全部纳入文章的累积档案（永不删除），
  `papers.js` 是网站用的展示数据。`data/seen_ids.json` 记录已处理过的文章，**不要删**，
  删了会导致下次全部重筛。

## 免责声明

自动筛选存在漏检与误检；"Transferable" 的迁移建议是模型生成的启发性提示，正式引用前请阅读原文核实。
