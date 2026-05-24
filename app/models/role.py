from app.models.db import get_db
import time

class RoleModel:
    """角色模型"""

    @staticmethod
    def create(name='', code='', description='', is_super=0, status=1):
        """创建角色"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO roles (name, code, description, is_super, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, code, description, is_super, status, now, now))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("创建角色失败:", e)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(role_id):
        """根据ID获取角色"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles WHERE id = ?', (role_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_code(code):
        """根据编码获取角色"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles WHERE code = ?', (code,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all():
        """获取所有角色"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles ORDER BY is_super DESC, id ASC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_list(page=1, page_size=20, keyword=''):
        """分页获取角色列表"""
        conn = get_db()
        cursor = conn.cursor()

        offset = (page - 1) * page_size
        if keyword:
            cursor.execute('''
                SELECT * FROM roles
                WHERE name LIKE ? OR code LIKE ?
                ORDER BY is_super DESC, id ASC
                LIMIT ? OFFSET ?
            ''', (f'%{keyword}%', f'%{keyword}%', page_size, offset))
            cursor.execute('''
                SELECT COUNT(*) FROM roles
                WHERE name LIKE ? OR code LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%'))
        else:
            cursor.execute('''
                SELECT * FROM roles
                ORDER BY is_super DESC, id ASC
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
            cursor.execute('SELECT COUNT(*) FROM roles')

        rows = cursor.fetchall()
        total = cursor.fetchone()[0]
        conn.close()
        return {
            'data': [dict(row) for row in rows],
            'total': total,
            'page': page,
            'page_size': page_size
        }

    @staticmethod
    def update(role_id, **kwargs):
        """更新角色"""
        conn = get_db()
        cursor = cursor = conn.cursor()
        try:
            kwargs['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
            params = list(kwargs.values()) + [role_id]
            cursor.execute(f'UPDATE roles SET {set_clause} WHERE id = ?', params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("更新角色失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(role_id):
        """删除角色（不能删除超级管理员）"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT is_super FROM roles WHERE id = ?', (role_id,))
            row = cursor.fetchone()
            if row and row['is_super'] == 1:
                return False

            cursor.execute('DELETE FROM roles WHERE id = ?', (role_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("删除角色失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def get_admin_roles(admin_id):
        """获取管理员的角色列表"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.* FROM roles r
            INNER JOIN admin_roles ar ON r.id = ar.role_id
            WHERE ar.admin_id = ?
        ''', (admin_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def set_admin_roles(admin_id, role_ids):
        """设置管理员的角色"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM admin_roles WHERE admin_id = ?', (admin_id,))
            for role_id in role_ids:
                cursor.execute('INSERT INTO admin_roles (admin_id, role_id) VALUES (?, ?)', (admin_id, role_id))
            conn.commit()
            return True
        except Exception as e:
            print("设置管理员角色失败:", e)
            return False
        finally:
            conn.close()