import hashlib
from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.cover import Cover


def compute_md5(file_data: bytes) -> str:
  """Считаем MD5-хэш содержимого файла."""
  return hashlib.md5(file_data).hexdigest()


def get_extension(filename: str, mime_type: str) -> str:
  """Определяем расширение файла по имени или MIME-типу."""
  ext = Path(secure_filename(filename)).suffix.lower()
  if ext:
    return ext

  mime_map = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
  }
  return mime_map.get(mime_type, ".img")


def save_cover(file: FileStorage, book_id: int, upload_folder: Path) -> Cover:
  """
  Сохраняем обложку книги.
  Если файл с таким MD5 уже есть — переиспользуем запись и копируем ссылку.
  """
  file_data = file.read()
  md5_hash = compute_md5(file_data)
  mime_type = file.mimetype or "application/octet-stream"

  # Проверяем, не загружали ли мы уже такой же файл
  existing = Cover.query.filter_by(md5_hash=md5_hash).first()
  if existing:
    # Такой файл уже есть на диске — создаём запись, но файл не перезаписываем
    cover = Cover(
      filename=existing.filename,
      mime_type=existing.mime_type,
      md5_hash=md5_hash,
      book_id=book_id,
    )
    db.session.add(cover)
    db.session.flush()
    return cover

  # Создаём новую запись — имя файла возьмём из id после flush
  cover = Cover(
    filename="temp",
    mime_type=mime_type,
    md5_hash=md5_hash,
    book_id=book_id,
  )
  db.session.add(cover)
  db.session.flush()

  ext = get_extension(file.filename or "", mime_type)
  cover.filename = f"{cover.id}{ext}"

  upload_folder.mkdir(parents=True, exist_ok=True)
  file_path = upload_folder / cover.filename
  file_path.write_bytes(file_data)

  return cover


def delete_cover_file(cover: Cover, upload_folder: Path) -> None:
  """Удаляем файл обложки с диска, если он больше нигде не используется."""
  if not cover:
    return

  # Проверяем, есть ли другие записи с тем же хэшем
  other = Cover.query.filter(
    Cover.md5_hash == cover.md5_hash,
    Cover.id != cover.id,
  ).first()

  if other:
    return

  file_path = upload_folder / cover.filename
  if file_path.exists():
    file_path.unlink()
