locals {
  parameters = {
    database_password = {
      description = "PostgreSQL master password"
      value       = random_password.database.result
    }
    jwt_secret = {
      description = "JWT signing secret"
      value       = random_password.jwt_secret.result
    }
    smtp_password = {
      description = "SMTP authentication password"
      value       = random_password.smtp_password.result
    }
    application_secret = {
      description = "Application encryption secret"
      value       = random_password.application_secret.result
    }
    openai_api_key = {
      description = "OpenAI API key"
      value       = var.openai_api_key
    }
  }
}
