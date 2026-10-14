"""Preserve the first original copy and replace saves only after writing succeeds."""
import os
import shutil
import tempfile


def ensure_backup(path):
    backup = os.fspath(path) + ".bak"
    try:
        with open(path, "rb") as source, open(backup, "xb") as target:
            try:
                shutil.copyfileobj(source, target)
            except BaseException:
                target.close()
                os.remove(backup)
                raise
    except FileExistsError:
        pass  # Never replace the original backup with a later edited save.
    return backup


def atomic_save(save, path):
    path = os.path.abspath(path)
    data = save.to_bytes()  # Serialize before opening/replacing the destination.
    fd, temporary = tempfile.mkstemp(prefix=".mw5-", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)
