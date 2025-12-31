# 開發階段索引

語音記帳助手的開發任務，按階段拆分。

---

## 階段總覽

| Phase | 名稱 | 說明 | 狀態 |
|-------|------|------|------|
| 0 | [重構專案結構](./phase-0-restructure.md) | 參考 note_money 建立新結構 | 🔲 待開始 |
| 1 | [後端核心功能](./phase-1-backend-core.md) | 記帳 API、LLM、Sheets | 🔲 待開始 |
| 2 | [Siri 捷徑整合](./phase-2-siri-integration.md) | API Token、Siri 設定文件 | 🔲 待開始 |
| 3 | [前端開發](./phase-3-frontend.md) | 網頁 UI、語音輸入/輸出 | 🔲 待開始 |
| 4 | [功能補強](./phase-4-enhancements.md) | 統計查詢、理財回饋 | 🔲 待開始 |
| 5 | [Google OAuth 2.0](./phase-5-oauth.md) | 用戶登入、專屬 Sheet | 🔲 待開始 |
| 6 | [部署與文件](./phase-6-deployment.md) | GCP 部署、README | 🔲 待開始 |

---

## 狀態說明

- 🔲 待開始
- 🔶 進行中
- ✅ 已完成

---

## 開發順序

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
   │         │         │         │         │         │         │
   │         │         │         │         │         │         └─ 上線
   │         │         │         │         │         └─ 多用戶支援
   │         │         │         │         └─ 統計與回饋
   │         │         │         └─ 網頁版可用
   │         │         └─ Siri 可用
   │         └─ API 可用
   └─ 專案結構就緒
```

---

## 快速里程碑

| 里程碑 | 完成 Phase | 可用功能 |
|--------|-----------|----------|
| MVP（最小可用） | 0, 1, 2 | Siri 語音記帳 |
| 網頁版 | + 3 | 網頁語音記帳 |
| 完整功能 | + 4 | 統計查詢、理財建議 |
| 多用戶 | + 5 | 用戶自己的 Sheet |
| 生產就緒 | + 6 | 正式上線 |

---

## 參考資源

- [task.md](../../task.md) - 完整專案規劃
- [note_money/](../../note_money/) - 現有功能參考（功能重現後刪除）
