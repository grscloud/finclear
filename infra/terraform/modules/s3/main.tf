#######################################
# 1. 创建 S3 存储桶 (通过变量区分前端和发票桶)
#######################################
resource "aws_s3_bucket" "buckets" {
  for_each = var.buckets

  bucket = each.value.bucket_name

  # tags = merge(var.tags, each.value.tags, {
  #   Name = each.value.bucket_name
  # })
}

#######################################
# 2. 版本控制 (两者都需要)
#######################################
resource "aws_s3_bucket_versioning" "buckets" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  versioning_configuration {
    status = "Enabled"
  }
}

#######################################
# 3. 服务端加密 (两者都需要)
#######################################
resource "aws_s3_bucket_server_side_encryption_configuration" "buckets" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

#######################################
# 4. 公共访问拦截 (针对不同桶做差异化处理)
#######################################
resource "aws_s3_bucket_public_access_block" "buckets" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  # 关键修改：
  # 如果是前端桶 (frontend)，允许通过 CloudFront OAC 访问，所以不能全封死。
  # 如果是发票桶 (application)，严格锁死，禁止任何外网直接读取。
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = each.key == "frontend" ? false : true 
}

#######################################
# 5. 生命周期规则 (区分前端与发票桶)
#######################################
resource "aws_s3_bucket_lifecycle_configuration" "buckets" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  # -----------------------------------------------------------------
  # 规则 A：仅针对【发票桶 (application)】的长期归档策略
  # -----------------------------------------------------------------
  dynamic "rule" {
    for_each = each.key == "application" ? [1] : []
    content {
      id     = "invoice-archive-glacier-ir"
      status = "Enabled"

      filter {}

      # 当前发票：90 天后转入冰川即时检索
      transition {
        days          = 90
        storage_class = "GLACIER_IR"
      }

      # 历史版本：30 天后转入冰川即时检索
      noncurrent_version_transition {
        noncurrent_days = 30
        storage_class   = "GLACIER_IR"
      }
    }
  }

  # -----------------------------------------------------------------
  # 规则 B：仅针对【前端桶 (frontend)】的清理策略（清理旧版本代码）
  # -----------------------------------------------------------------
  dynamic "rule" {
    for_each = each.key == "frontend" ? [1] : []
    content {
      id     = "frontend-cleanup-old-versions"
      status = "Enabled"

      filter {}

      # 前端代码经常频繁更新，自动清理 30 天以前的旧代码版本，省存储空间
      noncurrent_version_expiration {
        noncurrent_days = 30
      }
    }
  }

  # -----------------------------------------------------------------
  # 规则 C：公共规则（两个桶都需要）：清理上传中断的废弃碎片
  # -----------------------------------------------------------------
  rule {
    id     = "abort-incomplete-multipart-uploads"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

#######################################
# 6. CORS 配置 (针对需要浏览器直传的桶，例如发票桶 application)
#######################################
resource "aws_s3_bucket_cors_configuration" "buckets" {
  # 💡 修改点 1：简化 for_each 逻辑，明确只为 "application" (发票/应用桶) 启用 CORS
  for_each = { for k, v in aws_s3_bucket.buckets : k => v if k == "application" }

  # 💡 修改点 2：直接使用 each.value.id 获取桶 ID
  bucket = each.value.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "HEAD"]
    allowed_origins = [
      "https://finclear.grs-co.jp",
      # 为了方便本地开发时也能正常直传，建议把本地的开发端口也加上：
      "http://localhost:5173", 
      "http://localhost:3000"
    ]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}