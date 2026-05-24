from app.models.db import get_db

class DigitalWorkerModel:
    """数字员工模型"""

    @staticmethod
    def get_list(page=1, page_size=10, keyword='', worker_type=''):
        """分页获取数字员工列表"""
        conn = get_db()
        cursor = conn.cursor()

        offset = (page - 1) * page_size
        where_clauses = []
        params = []

        if keyword:
            where_clauses.append('(name LIKE ? OR alias LIKE ? OR description LIKE ?)')
            params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])

        if worker_type:
            where_clauses.append('worker_type = ?')
            params.append(worker_type)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        cursor.execute(f'''
            SELECT * FROM digital_workers
            WHERE {where_sql}
            ORDER BY is_default DESC, created_at DESC
            LIMIT ? OFFSET ?
        ''', params + [page_size, offset])
        rows = cursor.fetchall()

        cursor.execute(f'SELECT COUNT(*) FROM digital_workers WHERE {where_sql}', params)
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
    def get_by_id(worker_id):
        """根据ID获取数字员工"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM digital_workers WHERE id = ?', (worker_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_alias(alias):
        """根据别名获取数字员工"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM digital_workers WHERE alias = ?', (alias,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name, alias, worker_type, description='', avatar='', prompt=None,
               model_id=None, api_interface_id=None, response_mode='text',
               is_default=0, status=1):
        """创建数字员工"""
        conn = get_db()
        cursor = conn.cursor()
        import time
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            INSERT INTO digital_workers (name, alias, worker_type, description, avatar,
                                        prompt, model_id, api_interface_id, response_mode,
                                        is_default, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, alias, worker_type, description, avatar, prompt, model_id,
              api_interface_id, response_mode, is_default, status, now, now))

        worker_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return worker_id

    @staticmethod
    def update(worker_id, name, alias, worker_type, description='', avatar='',
               prompt=None, model_id=None, api_interface_id=None, response_mode='text',
               is_default=0, status=1):
        """更新数字员工"""
        conn = get_db()
        cursor = conn.cursor()
        import time
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            UPDATE digital_workers
            SET name = ?, alias = ?, worker_type = ?, description = ?, avatar = ?,
                prompt = ?, model_id = ?, api_interface_id = ?, response_mode = ?,
                is_default = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (name, alias, worker_type, description, avatar, prompt, model_id,
              api_interface_id, response_mode, is_default, status, now, worker_id))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete(worker_id):
        """删除数字员工"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM digital_workers WHERE id = ?', (worker_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_all(status=1):
        """获取所有数字员工"""
        conn = get_db()
        cursor = conn.cursor()
        if status is not None:
            cursor.execute('SELECT * FROM digital_workers WHERE status = ? ORDER BY is_default DESC, alias', (status,))
        else:
            cursor.execute('SELECT * FROM digital_workers ORDER BY is_default DESC, alias')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_default():
        """获取默认数字员工"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM digital_workers WHERE is_default = 1 AND status = 1')
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None