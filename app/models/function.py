from app.models.db import get_db
import time

class FunctionModel:
    """功能模型"""

    @staticmethod
    def create(parent_id=0, name='', code='', type='menu', icon='', url='#', sort_order=0, status=1):
        """创建功能"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO functions (parent_id, name, code, type, icon, url, sort_order, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (parent_id, name, code, type, icon, url, sort_order, status, now, now))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("创建功能失败:", e)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(func_id):
        """根据ID获取功能"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM functions WHERE id = ?', (func_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_code(code):
        """根据编码获取功能"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM functions WHERE code = ?', (code,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all():
        """获取所有功能"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM functions ORDER BY sort_order ASC, id ASC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_tree():
        """获取功能树形结构"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM functions ORDER BY sort_order ASC, id ASC')
        rows = cursor.fetchall()
        conn.close()
        functions = [dict(row) for row in rows]

        tree = []
        for func in functions:
            if func['parent_id'] == 0:
                children = [f for f in functions if f['parent_id'] == func['id']]
                func['children'] = children
                tree.append(func)
        return tree

    @staticmethod
    def get_by_parent(parent_id):
        """根据父ID获取子功能"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM functions WHERE parent_id = ? ORDER BY sort_order ASC', (parent_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_list(page=1, page_size=20, keyword=''):
        """分页获取功能列表"""
        conn = get_db()
        cursor = conn.cursor()

        offset = (page - 1) * page_size
        if keyword:
            cursor.execute('''
                SELECT * FROM functions
                WHERE name LIKE ? OR code LIKE ?
                ORDER BY sort_order ASC, id ASC
                LIMIT ? OFFSET ?
            ''', (f'%{keyword}%', f'%{keyword}%', page_size, offset))
            cursor.execute('''
                SELECT COUNT(*) FROM functions
                WHERE name LIKE ? OR code LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%'))
        else:
            cursor.execute('''
                SELECT * FROM functions
                ORDER BY sort_order ASC, id ASC
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
            cursor.execute('SELECT COUNT(*) FROM functions')

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
    def update(func_id, **kwargs):
        """更新功能"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            kwargs['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
            params = list(kwargs.values()) + [func_id]
            cursor.execute(f'UPDATE functions SET {set_clause} WHERE id = ?', params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("更新功能失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(func_id):
        """删除功能"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM functions WHERE id = ?', (func_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("删除功能失败:", e)
            return False
        finally:
            conn.close()