import json
from app.models.db import get_db

class ApiInterfaceModel:
    """API接口管理模型"""

    @staticmethod
    def get_list(page=1, page_size=10, keyword='', category=''):
        """分页获取接口列表"""
        conn = get_db()
        cursor = conn.cursor()

        offset = (page - 1) * page_size
        where_clauses = []
        params = []

        if keyword:
            where_clauses.append('(name LIKE ? OR code LIKE ? OR api_url LIKE ? OR description LIKE ?)')
            params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])

        if category:
            where_clauses.append('category = ?')
            params.append(category)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        cursor.execute(f'''
            SELECT * FROM api_interfaces
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', params + [page_size, offset])
        rows = cursor.fetchall()

        cursor.execute(f'SELECT COUNT(*) FROM api_interfaces WHERE {where_sql}', params)
        total_row = cursor.fetchone()
        total = total_row[0] if total_row else 0

        conn.close()
        return {
            'data': [dict(row) for row in rows],
            'total': total,
            'page': page,
            'page_size': page_size
        }

    @staticmethod
    def get_by_id(interface_id):
        """根据ID获取接口"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM api_interfaces WHERE id = ?', (interface_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_code(code):
        """根据code获取接口"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM api_interfaces WHERE code = ?', (code,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name, code, api_url, request_method='GET', response_format='JSON',
               description='', parameters=None, example='', qps_limit=4,
               token_required=0, category='other', status=1):
        """创建接口"""
        conn = get_db()
        cursor = conn.cursor()
        import time
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        parameters_str = json.dumps(parameters, ensure_ascii=False) if parameters else '[]'

        cursor.execute('''
            INSERT INTO api_interfaces (name, code, api_url, request_method, response_format,
                                      description, parameters, example, qps_limit, token_required,
                                      category, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, code, api_url, request_method, response_format, description,
              parameters_str, example, qps_limit, token_required, category, status, now, now))

        interface_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return interface_id

    @staticmethod
    def update(interface_id, name, code, api_url, request_method='GET',
               response_format='JSON', description='', parameters=None, example='',
               qps_limit=4, token_required=0, category='other', status=1):
        """更新接口"""
        conn = get_db()
        cursor = conn.cursor()
        import time
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        parameters_str = json.dumps(parameters, ensure_ascii=False) if parameters else '[]'

        cursor.execute('''
            UPDATE api_interfaces
            SET name = ?, code = ?, api_url = ?, request_method = ?, response_format = ?,
                description = ?, parameters = ?, example = ?, qps_limit = ?,
                token_required = ?, category = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (name, code, api_url, request_method, response_format, description,
              parameters_str, example, qps_limit, token_required, category, status, now, interface_id))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(interface_id):
        """删除接口"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM api_interfaces WHERE id = ?', (interface_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_all(status=1):
        """获取所有接口"""
        conn = get_db()
        cursor = conn.cursor()
        if status is not None:
            cursor.execute('SELECT * FROM api_interfaces WHERE status = ? ORDER BY category, name', (status,))
        else:
            cursor.execute('SELECT * FROM api_interfaces ORDER BY category, name')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_categories():
        """获取所有分类"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM api_interfaces WHERE category IS NOT NULL AND category != "" ORDER BY category')
        rows = cursor.fetchall()
        conn.close()
        return [row['category'] for row in rows]