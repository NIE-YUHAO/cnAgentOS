from app.models.db import get_db
import time
import requests
import json

class ModelModel:
    """模型管理模型"""

    @staticmethod
    def create(name, code, api_type='openai', api_base=None, api_key=None, model_name=None,
               max_tokens=4096, temperature=0.7, top_p=1.0, description=None):
        """创建模型"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO models (name, code, api_type, api_base, api_key, model_name,
                                   max_tokens, temperature, top_p, description,
                                   created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, code, api_type, api_base, api_key, model_name,
                  max_tokens, temperature, top_p, description,
                  time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("创建模型失败:", e)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(model_id):
        """根据ID获取模型"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM models WHERE id = ?', (model_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_code(code):
        """根据编码获取模型"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM models WHERE code = ?', (code,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all(status=None):
        """获取所有模型"""
        conn = get_db()
        cursor = conn.cursor()
        if status is not None:
            cursor.execute('SELECT * FROM models WHERE status = ? ORDER BY is_default DESC, created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM models ORDER BY is_default DESC, created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_list(page=1, page_size=6, keyword=''):
        """分页获取模型列表"""
        conn = get_db()
        cursor = conn.cursor()
        
        offset = (page - 1) * page_size
        if keyword:
            cursor.execute('''
                SELECT * FROM models 
                WHERE name LIKE ? OR code LIKE ? OR description LIKE ?
                ORDER BY is_default DESC, created_at DESC
                LIMIT ? OFFSET ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', page_size, offset))
            rows = cursor.fetchall()
            
            cursor.execute('''
                SELECT COUNT(*) FROM models 
                WHERE name LIKE ? OR code LIKE ? OR description LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            total_row = cursor.fetchone()
        else:
            cursor.execute('''
                SELECT * FROM models 
                ORDER BY is_default DESC, created_at DESC
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
            rows = cursor.fetchall()
            
            cursor.execute('SELECT COUNT(*) FROM models')
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
    def update(model_id, **kwargs):
        """更新模型"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            kwargs['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
            params = list(kwargs.values()) + [model_id]
            
            cursor.execute(f'UPDATE models SET {set_clause} WHERE id = ?', params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("更新模型失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(model_id):
        """删除模型"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            model = ModelModel.get_by_id(model_id)
            if model and model['is_default'] == 1:
                return False
            
            cursor.execute('DELETE FROM token_usage WHERE model_id = ?', (model_id,))
            cursor.execute('DELETE FROM models WHERE id = ?', (model_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("删除模型失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def set_default(model_id):
        """设置为默认模型"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE models SET is_default = 0')
            cursor.execute('UPDATE models SET is_default = 1 WHERE id = ?', (model_id,))
            conn.commit()
            return True
        except Exception as e:
            print("设置默认模型失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def get_default():
        """获取默认模型"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM models WHERE is_default = 1 AND status = 1')
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def call_api(model_id, messages, stream=False):
        """调用模型API（OpenAI API格式）"""
        model = ModelModel.get_by_id(model_id)
        if not model or model['status'] != 1:
            return None, '模型不存在或已禁用'

        try:
            url = f"{model['api_base'].rstrip('/')}/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {model['api_key']}"
            }
            
            data = {
                'model': model['model_name'],
                'messages': messages,
                'max_tokens': model['max_tokens'],
                'temperature': model['temperature'],
                'top_p': model['top_p'],
                'stream': stream,
                'stream_options': {'include_usage': True} if stream else {}
            }

            if stream:
                response = requests.post(url, headers=headers, json=data, stream=True, timeout=300)
                response.raise_for_status()
                return response, None
            else:
                response = requests.post(url, headers=headers, json=data, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                prompt_tokens = result.get('usage', {}).get('prompt_tokens', 0)
                completion_tokens = result.get('usage', {}).get('completion_tokens', 0)
                total_tokens = result.get('usage', {}).get('total_tokens', 0)
                
                TokenUsageModel.record_usage(model_id, prompt_tokens, completion_tokens, total_tokens)
                
                return result, None
                
        except requests.exceptions.RequestException as e:
            return None, f'网络请求失败: {str(e)}'
        except Exception as e:
            return None, f'调用失败: {str(e)}'

class TokenUsageModel:
    """Token使用统计模型"""

    @staticmethod
    def record_usage(model_id, prompt_tokens, completion_tokens, total_tokens):
        """记录Token使用"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            today = time.strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT * FROM token_usage WHERE model_id = ? AND usage_date = ?
            ''', (model_id, today))
            row = cursor.fetchone()
            
            if row:
                cursor.execute('''
                    UPDATE token_usage 
                    SET prompt_tokens = prompt_tokens + ?,
                        completion_tokens = completion_tokens + ?,
                        total_tokens = total_tokens + ?,
                        updated_at = ?
                    WHERE model_id = ? AND usage_date = ?
                ''', (prompt_tokens, completion_tokens, total_tokens, 
                      time.strftime('%Y-%m-%d %H:%M:%S'), model_id, today))
            else:
                cursor.execute('''
                    INSERT INTO token_usage (model_id, prompt_tokens, completion_tokens, 
                                           total_tokens, usage_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (model_id, prompt_tokens, completion_tokens, 
                      total_tokens, today, time.strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            return True
        except Exception as e:
            print("记录Token使用失败:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def get_by_model(model_id, days=7):
        """获取模型的Token使用统计"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT usage_date, prompt_tokens, completion_tokens, total_tokens
                FROM token_usage 
                WHERE model_id = ? 
                ORDER BY usage_date DESC 
                LIMIT ?
            ''', (model_id, days))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print("获取Token统计失败:", e)
            return []
        finally:
            conn.close()

    @staticmethod
    def get_summary(model_id=None):
        """获取Token使用汇总"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            if model_id:
                cursor.execute('''
                    SELECT SUM(prompt_tokens) as total_prompt, 
                           SUM(completion_tokens) as total_completion,
                           SUM(total_tokens) as total
                    FROM token_usage WHERE model_id = ?
                ''', (model_id,))
            else:
                cursor.execute('''
                    SELECT SUM(prompt_tokens) as total_prompt, 
                           SUM(completion_tokens) as total_completion,
                           SUM(total_tokens) as total
                    FROM token_usage
                ''')
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print("获取Token汇总失败:", e)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_daily_summary(days=7):
        """获取每日汇总统计"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT usage_date, 
                       SUM(prompt_tokens) as prompt_tokens, 
                       SUM(completion_tokens) as completion_tokens,
                       SUM(total_tokens) as total_tokens
                FROM token_usage 
                GROUP BY usage_date 
                ORDER BY usage_date DESC 
                LIMIT ?
            ''', (days,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print("获取每日汇总失败:", e)
            return []
        finally:
            conn.close()