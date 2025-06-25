# 禮品碼批量兌換系統

一個用於批量兌換遊戲禮品碼的自動化工具。

## 主要功能

### 1. 基礎功能
- [x] 支持多個用戶 ID 輸入（逗號分隔）
- [x] 支持多個禮品碼輸入（逗號分隔）
- [x] 自動處理驗證碼
- [x] 顯示詳細的兌換結果
- [x] 支持從 .env 文件讀取預設用戶 ID

### 2. 並行處理
- [x] 批次處理請求（每批 3 個並行）
- [x] 自動控制請求頻率（批次間延遲 500ms）
- [x] 用戶間處理延遲（1000ms）
- [x] 顯示總體處理進度

### 3. 錯誤處理
- [x] 驗證碼錯誤自動重試
- [x] 記錄失敗的兌換嘗試
- [x] 支持失敗項目重試功能
- [x] 顯示詳細的錯誤信息

### 4. 用戶界面
- [x] 清空用戶 ID 按鈕
- [x] 停止處理按鈕
- [x] 重試失敗項目按鈕
- [x] 響應式設計（支持手機訪問）
- [x] 進度顯示
- [x] 可展開的詳細信息

### 5. 部署相關
- [x] Docker 容器化
- [x] Nginx 反向代理支持
- [x] 環境變量配置
- [x] 域名訪問支持

## 環境變量配置

```env
# API URLs
CAPTCHA_BASE_URL=https://prod-mail.habbyservice.com/Capybara/api/v1/captcha
CAPTCHA_GENERATE_URL=https://prod-mail.habbyservice.com/Capybara/api/v1/captcha/generate
CLAIM_API_URL=https://prod-mail.habbyservice.com/Capybara/api/v1/giftcode/claim

# 預先定義要發放的user
DEFAULT_USER_IDS=user1,user2,user3

# Server settings
PORT=8000
HOST=0.0.0.0
```

## 使用說明

1. 啟動服務：
```bash
docker-compose up --build -d
```

2. 訪問：
- 開發環境：http://localhost:8500/static/index.html

3. 使用方法：
   - 輸入用戶 ID（多個用逗號分隔）
   - 輸入禮品碼（多個用逗號分隔）
   - 點擊「批量兌換禮品碼」開始處理
   - 可以隨時點擊「停止兌換」
   - 失敗的項目可以點擊「重試失敗項目」重新處理

## 注意事項

1. 並行請求限制：
   - 每批次同時處理 3 個請求
   - 批次間延遲 500ms
   - 用戶間延遲 1000ms

2. 錯誤處理：
   - 驗證碼錯誤會自動重試
   - 其他錯誤會記錄並支持手動重試

3. 安全性：
   - 生產環境建議限制 CORS
   - 建議添加請求頻率限制
   - 建議添加訪問日誌