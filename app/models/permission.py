from app.models.db import get_db
import time

class PermissionModel:
    """权限模型"""

    @staticmethod
    def create(role_id, function_id):
        """创建权限"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO permissions (role_id, function_id, created_at)
                VALUES (?, ?, ?)
            ''', (role_id, function_id, now))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("创建权限失败:", e)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_role(role_id):
        """获取角色的所有权限"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.* FROM functions f
            INNER JOIN permissions p ON f.id = p.function_id
            WHERE p.role_id = ?
            ORDER BY f.sort_order ASC
        ''', (role_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_role_codes(role_ids):
        """根据角色ID列表获取所有权限"""
        if not role_ids:
            return []
        conn = get_db()
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(role_ids))
        cursor.execute(f'''
            SELECT DISTINCT f.* FROM functions f
            INNER JOIN permissions p ON f.id = p.function_id
            WHERE p.role_id IN ({placeholders})
            ORDER BY f.sort_order ASC
        ''', role_ids)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def set_role_permissions(role_id, function_ids):
        """设置角色的权限"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM permissions WHERE role_id = ?', (role_id,))
            for func_id in function_ids:
                cursor.execute('''
                    INSERT INTO permissions (role_id, function_id, created_at)
                    VALUES (?, ?, ?)
                ''', (role_id, func_id, time.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            return True
        except Exception as e:
            print("设置角色权限失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(role_id, function_id):
        """删除指定权限"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM permissions WHERE role_id = ? AND function_id = ?', (role_id, function_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("删除权限失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def delete_by_role(role_id):
        """删除角色的所有权限"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM permissions WHERE role_id = ?', (role_id,))
            conn.commit()
            return True
        except Exception as e:
            print("删除角色权限失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def check_permission(role_ids, function_code):
        """检查角色是否有指定功能的权限"""
        if not role_ids:
            return False
        conn = get_db()
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(role_ids))
        cursor.execute(f'''
            SELECT COUNT(*) FROM permissions p
            INNER JOIN functions f ON p.function_id = f.id
            WHERE p.role_id IN ({placeholders}) AND f.code = ?
        ''', role_ids + [function_code])
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0