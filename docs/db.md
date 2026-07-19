---
🛠️ モジュール1：マルチテナント ＆ RBAC権限管理体系
---
1. companies（テナント・企業マスタ）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,テナント一意識別子
name,VARCHAR,NOT NULL,企業名・会社名
invoice_number,VARCHAR(14),NULL,適格請求書発行事業者登録番号（T + 13桁の数字）
created_at,TIMESTAMP,DEFAULT NOW(),作成日時

2. users（ユーザーマスタ：AWS Cognito連携）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,AWS Cognitoの sub を直接マッピング
email,VARCHAR,"UNIQUE, NOT NULL",ログイン用メールアドレス
status,VARCHAR,NOT NULL,"ステータス：active (有効), invited (招待中), suspended (アカウント停止)"

3. permissions（権限マスタ：コード管理用、画面なし）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,INT,PRIMARY KEY,自動インクリメントID
code,VARCHAR,"UNIQUE, NOT NULL","権限コード（例：expense:approve, invoice:create）"
name,VARCHAR,NOT NULL,権限名・説明（例：「経費承認」、「請求書作成」）

4. roles（ロールマスタ）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,INT,PRIMARY KEY,自動インクリメントID
code,VARCHAR,"UNIQUE, NOT NULL","ロールコード：company_admin, employee, guest, super_admin"
name,VARCHAR,NOT NULL,ロール名（例：「会社管理者」、「一般社員」）

5. role_permissions（ロール・権限マッピング表）
カラム名 (物理名),データ型,制約 / インデックス,説明
role_id,INT,FOREIGN KEY,roles.id に関連付け
permission_id,INT,FOREIGN KEY,permissions.id に関連付け
複合主キー,"(role_id, permission_id)",—,—

6. tenant_user_roles（テナント・ユーザー・ロール紐付け表：コア解耦ポイント）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,リレーションID
company_id,UUID,"FOREIGN KEY, INDEX",companies.id に関連付け
user_id,UUID,"FOREIGN KEY, INDEX",users.id に関連付け
role_id,INT,FOREIGN KEY,roles.id に関連付け

---
🧾 モジュール2：商品マスタ ＆ 見積・請求書モジュール（インボイス制度対応）
---
7. products（商品・サービスマスタ）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,商品ID
company_id,UUID,"FOREIGN KEY, INDEX",所属会社（テナントID）
name,VARCHAR,NOT NULL,商品・サービス名（例：システム開発費）
default_price,NUMERIC,NOT NULL,デフォルト単価
tax_rate,INT,NOT NULL,"税率：10 (10%), 8 (8%), 0 (免税/非課税)"

8. clients（顧客マスタ）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,顧客ID
company_id,UUID,"FOREIGN KEY, INDEX",所属会社（テナントID）
name,VARCHAR,NOT NULL,顧客企業（正式名称）
invoice_number,VARCHAR(14),NULL,顧客の適格請求書発行事業者登録番号（T番号）

9. invoices（請求書・見積書ヘッダ表）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,帳票ID
company_id,UUID,"FOREIGN KEY, INDEX",テナント分離用ID
client_id,UUID,FOREIGN KEY,clients.id に関連付け
doc_type,VARCHAR,NOT NULL,帳票種別：estimate (見積書) / invoice (請求書)
doc_number,VARCHAR,"UNIQUE, NOT NULL",帳票番号（例：INV-202607-001）
issue_date,DATE,NOT NULL,発行日
due_date,DATE,NULL,支払期限
tax_base_10,NUMERIC,DEFAULT 0,10%対象の税抜合計金額
tax_amount_10,NUMERIC,DEFAULT 0,10%対象の消費税合計額（インボイス制度に基づき、1枚の請求書につきここでのみ端数処理を1回行う）
tax_base_8,NUMERIC,DEFAULT 0,8%対象の税抜合計金額
tax_amount_8,NUMERIC,DEFAULT 0,8%対象の消費税合計額
total_amount,NUMERIC,NOT NULL,最終税込合計金額

10. invoice_items（請求書・見積書明細表：💡 スナップショット設計）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,明細ID
invoice_id,UUID,"FOREIGN KEY, INDEX",invoices.id に関連付け
product_id,UUID,"FOREIGN KEY, NULL",元の商品ID（手入力によるカスタム項目を許可するため NULL 可）
name,VARCHAR,NOT NULL,スナップショット：発行時点の商品名・サービス名
unit_price,NUMERIC,NOT NULL,スナップショット：発行時点の単価
quantity,NUMERIC,NOT NULL,数量
tax_rate,INT,NOT NULL,スナップショット：発行時点の税率
subtotal,NUMERIC,NOT NULL,行ごとの税抜小計金額 (unit_price × quantity)

---
📸 モジュール3：経費管理 ＆ 承認フロー（電帳法・交通費特例対応）
---
11. expenses（経費ヘッダ表）
⚠️ 電子帳簿保存法（電帳法）対応の重要要件：法的要件である「複合条件による検索機能」を満たすため、必ず company_id, trans_date, vendor_name, total_amount による複合インデックスを構築してください。
字段名 (物理名),数据类型,约束 / 索引,说明
id,UUID,PRIMARY KEY,经费ID
company_id,UUID,FOREIGN KEY,租户ID（复合索引构成要素1）
user_id,UUID,FOREIGN KEY,申请者ID
trans_date,DATE,"NOT NULL, INDEX",交易日期（复合索引构成要素2 —— 电帐法要件1）
vendor_name,VARCHAR,"NOT NULL, INDEX",交易方/店铺名（复合索引构成要素3 —— 电帐法要件2）
total_amount,NUMERIC,"NOT NULL, INDEX",含税总金额（复合索引构成要素4 —— 电帐法要件3）
tax_8_amount,NUMERIC,DEFAULT 0,8%税率的金额部分（轻减税率）
tax_10_amount,NUMERIC,DEFAULT 0,10%税率的金额部分（标准税率）
category,VARCHAR,NOT NULL,"大类：general (一般费用), transportation (交通费)"
account_item_id,UUID,NULL,财务科目ID（如：会议费、差旅费，关联科目字典表）
t_number,VARCHAR(14),NULL,供应商 Invoice 注册号 (适格请求书判定用)
invoice_type,VARCHAR,NOT NULL,"发票类型：qualified (适格), non_qualified (免税/非适格)"
deduction_rate,NUMERIC,NOT NULL,"进项税抵扣比例 (例如：1.0, 0.8, 0.5 应对过渡期政策)"
status,VARCHAR,NOT NULL,"状态：draft, pending, approved, rejected, canceled"
purpose,VARCHAR,NULL,报销目的 / 备注
created_at,TIMESTAMP,DEFAULT NOW(),创建时间
updated_at,TIMESTAMP,DEFAULT NOW(),更新时间
deleted_at,TIMESTAMP,NULL,软删除时间（电帐法防篡改/历史保留要求）

12. expense_receipts（証憑画像表：💡 AI連携 ＆ 改ざん防止監査ログ）
字段名 (物理名),数据类型,约束 / 索引,说明
id,UUID,PRIMARY KEY,凭证附件ID
expense_id,UUID,"FOREIGN KEY, INDEX",关联 expenses.id (1:N 关系)
original_filename,VARCHAR,NOT NULL,用户上传时的原始文件名
mime_type,VARCHAR,NOT NULL,"文件类型 (如 image/jpeg, application/pdf)"
file_size,INTEGER,NOT NULL,文件大小 (Bytes)
raw_s3_key,VARCHAR,NOT NULL,S3上的原始文件路径（只读，禁止修改，审计用）
proc_s3_key,VARCHAR,NULL,处理后的图片路径（裁切、增强对比度等）
ocr_raw_json,JSONB,NULL,LLM Vision 识别出的原始数据快照，用于高风险报销核对
created_at,TIMESTAMP,DEFAULT NOW(),上传时间
deleted_at,TIMESTAMP,NULL,软删除时间

13. expense_transport_details（交通費詳細拡張表：💡 1:1 業務データ分離）
字段名 (物理名),数据类型,约束 / 索引,说明
id,UUID,PRIMARY KEY,明细ID
expense_id,UUID,"FOREIGN KEY, INDEX",关联 expenses.id (注意：无 UNIQUE 约束，支持多段行程)
seq_num,INTEGER,NOT NULL,"行程序号（1, 2, 3... 保证前端渲染和导出的顺序）"
origin,VARCHAR,NOT NULL,出发地 / 车站（例：新宿駅）
destination,VARCHAR,NOT NULL,目的地 / 车站（例：渋谷駅）
amount,NUMERIC,NOT NULL,该段行程的金额
is_round_trip,BOOLEAN,DEFAULT FALSE,是否往返（若勾选往返，前端应自动计算双倍金额或生成回程记录）
input_method,VARCHAR,NOT NULL,"数据来源：manual (手写), route_search (API查路线), ic_card (Suica读取)"

14. expense_approvals（承認履歴・ワークフローログ表）
字段名 (物理名),数据类型,约束 / 索引,说明
id,UUID,PRIMARY KEY,审批日志ID
expense_id,UUID,"FOREIGN KEY, INDEX",关联 expenses.id
operator_id,UUID,FOREIGN KEY,操作者ID (申请人、审批人、财务)
action,VARCHAR,NOT NULL,"操作：submit (提交), approve (同意), reject (退回), cancel (撤销)"
comment,TEXT,NULL,驳回理由或审批意见（满足电帐法“订正删除需留痕”的要求）
created_at,TIMESTAMP,DEFAULT NOW(),审批操作发生的精确时间

---
💴 モジュール4：役員報酬・給与モジュール（定期同額給与対応）
---
15. salary_settings（給与・報酬基準設定表）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,設定ID
company_id,UUID,FOREIGN KEY,テナント分離用ID
user_id,UUID,FOREIGN KEY,対象の役員 / 社員
base_salary,NUMERIC,NOT NULL,固定月給 / 役員報酬額（日本の税法上の「定期同額給与」の原則に準拠）
fiscal_year,INT,NOT NULL,適用事業年度 / 会計年度（例：2026）
start_date,DATE,NOT NULL,支給開始日（適用開始日）
end_date,DATE,NOT NULL,支給終了日（適用終了日）

16. salary_slips（月次給与明細表）
カラム名 (物理名),データ型,制約 / インデックス,説明
id,UUID,PRIMARY KEY,給与明細ID
company_id,UUID,FOREIGN KEY,テナント分離用ID
user_id,UUID,FOREIGN KEY,支給対象者
target_month,VARCHAR(7),INDEX,"支給対象月（フォーマット例：""2026-07""）"
base_salary,NUMERIC,NOT NULL,スナップショット：該当月に支給された固定基本給 / 役員報酬額
health_insurance,NUMERIC,DEFAULT 0,控除：健康保険料
welfare_pension,NUMERIC,DEFAULT 0,控除：厚生年金保険料
withholding_tax,NUMERIC,DEFAULT 0,控除：源泉所得税
net_pay,NUMERIC,NOT NULL,差引支給額 / 手取り金額（base_salary - 各種控除項目の合計）
created_at,TIMESTAMP,DEFAULT NOW(),明細生成日時

