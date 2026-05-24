import json
from app.models.db import get_db

class ObservationSourceModel:
    """瞭望数据源模型"""

    @staticmethod
    def get_list(page=1, page_size=10, keyword=''):
        """分页获取数据源列表"""
        conn = get_db()
        cursor = conn.cursor()

        offset = (page - 1) * page_size
        if keyword:
            cursor.execute('''
                SELECT * FROM observation_sources
                WHERE name LIKE ? OR code LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', page_size, offset))
            rows = cursor.fetchall()

            cursor.execute('''
                SELECT COUNT(*) FROM observation_sources
                WHERE name LIKE ? OR code LIKE ? OR description LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            total_row = cursor.fetchone()
        else:
            cursor.execute('''
                SELECT * FROM observation_sources
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
            rows = cursor.fetchall()

            cursor.execute('SELECT COUNT(*) FROM observation_sources')
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
    def get_by_id(source_id):
        """根据ID获取数据源"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM observation_sources WHERE id = ?', (source_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_code(code):
        """根据code获取数据源"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM observation_sources WHERE code = ?', (code,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name, code, source_type, entry_url, request_method='GET', headers=None,
               params_template=None, encoding='utf-8', parse_rule=None, description='', status=1):
        """创建数据源"""
        conn = get_db()
        cursor = conn.cursor()
        import time
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        headers_str = json.dumps(headers, ensure_ascii=False) if headers else None
        params_str = json.dumps(params_template, ensure_ascii=False) if params_template else None
        parse_rule_str = json.dumps(parse_rule, ensure_ascii=False) if parse_rule else None

        cursor.execute('''
            INSERT INTO observation_sources (name, code, source_type, entry_url, request_method,
                                           headers, params_template, encoding, parse_rule,
                                           description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, code, source_type, entry_url, request_method, headers_str,
              params_str, encoding, parse_rule_str, description, status, now, now))

        source_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return source_id

    @staticmethod
    def update(source_id, name, code, source_type, entry_url, request_method='GET',
               headers=None, params_template=None, encoding='utf-8', parse_rule=None,
               description='', status=1):
        """更新数据源"""
        conn = get_db()
        cursor = conn.cursor()
        import time
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        headers_str = json.dumps(headers, ensure_ascii=False) if headers else None
        params_str = json.dumps(params_template, ensure_ascii=False) if params_template else None
        parse_rule_str = json.dumps(parse_rule, ensure_ascii=False) if parse_rule else None

        cursor.execute('''
            UPDATE observation_sources
            SET name = ?, code = ?, source_type = ?, entry_url = ?, request_method = ?,
                headers = ?, params_template = ?, encoding = ?, parse_rule = ?,
                description = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (name, code, source_type, entry_url, request_method, headers_str,
              params_str, encoding, parse_rule_str, description, status, now, source_id))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(source_id):
        """删除数据源"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM observation_sources WHERE id = ?', (source_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_all():
        """获取所有启用的数据源"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM observation_sources WHERE status = 1 ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]