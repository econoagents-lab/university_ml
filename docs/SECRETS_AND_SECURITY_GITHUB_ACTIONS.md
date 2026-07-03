# Secrets y seguridad para GitHub Actions

## Secrets recomendados

```text
REDSHIFT_HOST
REDSHIFT_PORT
REDSHIFT_DATABASE
REDSHIFT_USER
REDSHIFT_PASSWORD
SLACK_WEBHOOK_URL
DISCORD_WEBHOOK_URL
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
MLU_RAILWAY_BASE_URL
MLU_API_KEY
```

## Reglas

1. Yo nunca subo `.env`.
2. Yo nunca indexo credenciales dentro del RAG.
3. Yo nunca envío DNI, teléfonos ni clientes reales por alerta pública.
4. Yo uso self-hosted runner para CRM privado.
5. Yo uso Railway para endpoints y demos, no para publicar secretos.

## Qué hago si expuse una credencial

1. Yo roto la credencial.
2. Yo elimino el archivo del repo.
3. Yo reviso historial Git si fue commiteado.
4. Yo actualizo secrets.
5. Yo regenero artifacts seguros.
