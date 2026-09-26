# 体成分变化趋势

xym / gcc 两人的 InBody 体成分数据可视化网页。纯静态，靠 GitHub Pages 托管。

## 文件说明

| 文件 | 作用 |
|---|---|
| `index.html` | 网页本体，加载 `data.js` 显示数据 |
| `data.js` | **数据文件（唯一数据源）**，所有体测记录都在这里 |
| `README.md` | 本说明 |

## 怎么加数据（改 `data.js`）

在 GitHub 网页上点开 `data.js` → 点右上角 **铅笔图标** 编辑 → 加好后 **Commit changes**，网页刷新即更新。

文件结构：

```js
const DATA = {
  xym: { title:"xym", records: [ {date, weight, muscle, ...}, ... ] },
  gcc: { title:"gcc", records: [ {date, weight, muscle, ...}, ... ] }
};
```

- 给某人加一次体测：在对应的 `records: [ ... ]` 数组里**追加**一条 `{...}` 对象（放在最后一个 `}` 之后、`]` 之前，注意用逗号隔开）。
- 一条记录的字段：

```js
{
  date:"10月10日 09:30",
  weight:62.9, muscle:26.3, fatMass:15.2, fatPct:24.1, water:34.9,
  protein:9.4, mineral:3.3, leanMass:47.7, bmi:23.7, visceral:6, bmr:1401,
  segMuscle:   {左臂:2.4,右臂:2.4,躯干:20.8,左腿:6.8,右腿:6.8},
  segFat:      {左臂:0.9,右臂:0.9,躯干:7.7, 左腿:2.3,右腿:2.3},
  segMusclePct:{左臂:115.7,右臂:112.8,躯干:107, 左腿:101.1,右腿:101.3},
  segFatPct:   {左臂:92.9,右臂:94.5,躯干:143.9,左腿:93.5,右腿:93.5},
  idealWeight:62.0, calorie:2187, goalWeight:-0.9, goalFat:-0.9, goalMuscle:0
}
```

> ⚠️ 只改数字和 `date`，**别动结构**（逗号、引号、大括号）。少一个符号页面会白屏。
> 不确定的项可以填 `null`（该点会断线）或照上一条复制。

## 部署到 GitHub Pages

1. 仓库 **Settings → Pages**。
2. Source 选 **Deploy from a branch**，Branch 选 **main**，目录 **/ (root)**，保存。
3. 稍等 1–2 分钟，访问 `https://<你的用户名>.github.io/<仓库名>/`。

## 字段含义

- 基础：体重、骨骼肌量、体脂肪量、体脂肪率、水分、蛋白质、矿物质、去脂体重、BMI、内脏脂肪等级、基础代谢（bmr）
- 身体节段：左臂/右臂/躯干/左腿/右腿 的 肌肉(`segMuscle`)、脂肪(`segFat`)、以及相对标准的百分比(`segMusclePct` / `segFatPct`)
- 目标：理想体重(`idealWeight`)、每日建议热量(`calorie`)、建议减体重/脂肪/肌肉(`goalWeight` / `goalFat` / `goalMuscle`)

> ⚠️ 本仓库内容公开在 GitHub 上，体测数据等于公开。
