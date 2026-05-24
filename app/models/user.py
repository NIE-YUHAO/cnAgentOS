from app.models.db import get_db

class UserModel:
    @staticmethod
    def create(username, password_hash):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("创建用户失败:", e)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_username(username):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None