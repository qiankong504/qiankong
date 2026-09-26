# 体成分变化趋势

xym / gcc 两人的 InBody 体成分数据可视化网页。纯静态，无需构建，靠 GitHub Pages 托管。

## 文件说明

| 文件 | 作用 |
|---|---|
| `index.html` | 网页本体（入口），加载 `data.js` |
| `data.js` | 网页数据，**由脚本自动生成，不要手改** |
| `体测数据.xlsx` | 数据源：每人一个工作表，一行 = 一次体测 |
| `表格转网页数据.py` | 转换脚本：读 xlsx → 生成 data.js |
| `.github/workflows/build-data.yml` | 自动化：推送 xlsx 后自动重生成 data.js |

## 日常更新数据（推荐流程）

1. 在 `体测数据.xlsx` 对应工作表（xym / gcc）最下面**加一行**，按列填数字。
2. 把 `体测数据.xlsx` 上传/推送到本仓库。
3. 稍等一会儿，GitHub Actions 会自动跑脚本、更新 `data.js` 并提交回来。
4. 刷新网页即可看到新数据。

> 也可以在网页上手动触发：仓库 **Actions → “从表格生成 data.js” → Run workflow**。

## 本地手动生成（可选）

```bash
pip install openpyxl
python3 表格转网页数据.py     # 生成 data.js
```
然后在浏览器打开 `index.html` 查看。

## 部署到 GitHub Pages

1. 仓库 **Settings → Pages**。
2. Source 选 **Deploy from a branch**，Branch 选 **main**，目录 **/ (root)**，保存。
3. 稍等 1–2 分钟，访问 `https://<你的用户名>.github.io/<仓库名>/`。

## 表格列说明（共 37 列）

- 基础 12 列：体测时间、体重、骨骼肌量、体脂肪量、体脂肪率、水分、蛋白质、矿物质、去脂体重、BMI、内脏脂肪、基础代谢
- 身体节段 20 列：左臂/右臂/躯干/左腿/右腿 的 肌肉(kg)、脂肪(kg)、肌肉(%)、脂肪(%)
- 目标 5 列：理想体重、每日建议热量、建议减体重、建议减脂肪、建议减肌肉

> ⚠️ 本仓库内容会公开在 GitHub 上。若不想公开体测数据，请勿上传 xlsx / data.js 到公开仓库。
