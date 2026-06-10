import bleach
import markdown as md

# Разрешённые HTML-теги после конвертации Markdown
ALLOWED_TAGS = [
  "p", "br", "strong", "em", "u", "s", "h1", "h2", "h3", "h4", "h5", "h6",
  "ul", "ol", "li", "blockquote", "code", "pre", "a", "img", "hr",
]
ALLOWED_ATTRIBUTES = {
  "a": ["href", "title"],
  "img": ["src", "alt", "title"],
}


def sanitize_markdown(text: str) -> str:
  """
  Очищаем введённый Markdown от опасных конструкций.
  Сохраняем исходный текст, а не HTML — конвертация будет при выводе.
  """
  if not text:
    return ""
  # Bleach убирает скрипты и прочие опасные теги, если пользователь их вставил
  return bleach.clean(text, tags=[], attributes={}, strip=True)


def render_markdown(text: str) -> str:
  """Преобразуем Markdown в безопасный HTML для отображения на странице."""
  if not text:
    return ""
  html = md.markdown(text, extensions=["extra", "nl2br"])
  return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
