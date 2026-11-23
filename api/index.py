# -*- coding: utf-8 -*-
"""Единая точка входа для Vercel Python runtime.

Vercel требует один entrypoint, когда в api/ несколько .py с app.
Этот роутер просто передаёт запрос в нужный модуль.
"""

from api import webhook, miniapp, cron


def app(environ, start_response):
    path = (environ.get("PATH_INFO") or "/").rstrip("/") or "/"

    if path == "/api/cron" or path.endswith("/cron"):
        return cron.app(environ, start_response)
    if path == "/api/miniapp" or path.startswith("/api/miniapp/"):
        return miniapp.app(environ, start_response)
    # /api/webhook, /api/webhook/..., и всё остальное — бот
    return webhook.app(environ, start_response)
