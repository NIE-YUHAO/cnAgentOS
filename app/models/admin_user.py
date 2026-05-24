from app.models.db import get_db
import bcrypt
import time

class AdminUserModel:
    """管理员用户模型"""
    
    @staticmethod
    def create(username, password, email=None, role='admin', status=1):
        """创建管理员用户（兼容旧接口）"""
        return AdminUserModel.create_with_role(username, password, email, 1, status)
    
    @staticmethod
    def create_with_role(username, password, email=None, role_id=1, status=1):
        """创建管理员用户并关联角色"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('''
                INSERT INTO admin_users (username, password_hash, email, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, email, status, time.strftime('%Y-%m-%d %H:%M:%S')))
            user_id = cursor.lastrowid
            
            if role_id:
                cursor.execute('''
                    INSERT INTO admin_roles (admin_id, role_id, created_at)
                    VALUES (?, ?, ?)
                ''', (user_id, role_id, time.strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            return user_id
        except Exception as e:
            print("创建管理员失败:", e)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        """根据ID获取管理员"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin_users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_username(username):
        """根据用户名获取管理员"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin_users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def verify_password(user, password):
        """验证密码"""
        if not user or not user.get('password_hash'):
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
    
    @staticmethod
    def get_list(page=1, page_size=20, keyword=''):
        """分页获取管理员列表（兼容旧接口）"""
        return AdminUserModel.get_list_with_role(page, page_size, keyword)
    
    @staticmethod
    def get_list_with_role(page=1, page_size=20, keyword=''):
        """分页获取管理员列表（包含角色信息）"""
        conn = get_db()
        cursor = conn.cursor()
        
        offset = (page - 1) * page_size
        if keyword:
            cursor.execute('''
                SELECT u.*, r.name as role_name, r.code as role_code 
                FROM admin_users u
                LEFT JOIN admin_roles ar ON u.id = ar.admin_id
                LEFT JOIN roles r ON ar.role_id = r.id
                WHERE u.username LIKE ? OR u.email LIKE ? 
                ORDER BY u.created_at DESC 
                LIMIT ? OFFSET ?
            ''', (f'%{keyword}%', f'%{keyword}%', page_size, offset))
            cursor.execute('''
                SELECT COUNT(*) FROM admin_users u
                WHERE u.username LIKE ? OR u.email LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%'))
        else:
            cursor.execute('''
                SELECT u.*, r.name as role_name, r.code as role_code 
                FROM admin_users u
                LEFT JOIN admin_roles ar ON u.id = ar.admin_id
                LEFT JOIN roles r ON ar.role_id = r.id
                ORDER BY u.created_at DESC 
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
            cursor.execute('SELECT COUNT(*) FROM admin_users')
        
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
    def update(user_id, **kwargs):
        """更新管理员信息"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            if 'password' in kwargs and kwargs['password']:
                kwargs['password_hash'] = bcrypt.hashpw(kwargs.pop('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            kwargs['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
            params = list(kwargs.values()) + [user_id]
            
            cursor.execute(f'UPDATE admin_users SET {set_clause} WHERE id = ?', params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("更新管理员失败:", e)
            return False
        finally:
            conn.close()
    
    @staticmethod
    def update_password(user_id, password):
        """仅更新密码"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('''
                UPDATE admin_users SET password_hash = ?, updated_at = ? WHERE id = ?
            ''', (password_hash, time.strftime('%Y-%m-%d %H:%M:%S'), user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("更新密码失败:", e)
            return False
        finally:
            conn.close()
    
    @staticmethod
    def update_role(user_id, role_id):
        """更新用户角色"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM admin_roles WHERE admin_id = ?', (user_id,))
            cursor.execute('''
                INSERT INTO admin_roles (admin_id, role_id, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, role_id, time.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            return True
        except Exception as e:
            print("更新角色失败:", e)
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(user_id):
        """删除管理员"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM admin_users WHERE id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("删除管理员失败:", e)
            return False
        finally:
            conn.close()
    
    @staticmethod
    def batch_delete(user_ids):
        """批量删除管理员"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            placeholders = ','.join('?' * len(user_ids))
            cursor.execute(f'DELETE FROM admin_users WHERE id IN ({placeholders})', user_ids)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print("批量删除管理员失败:", e)
            return 0
        finally:
            conn.close()