# ==========================================
# ⏳ 时间之神：处理历史沉淀
# ==========================================
def process_time_decay():
    """
    模拟时间的流逝：
    1. 找到所有 'active' 的节点。
    2. 如果节点太老 (比如超过 1 天)，将其转为 'sedimented' (沉积)。
    3. 返回沉积了多少个节点。
    
    (注意：为了在 Supabase 简单实现，我们利用 'mode' 字段来标记状态)
    mode='News' -> 活跃新闻
    mode='Sediment' -> 历史沉积
    """
    try:
        # 1. 获取所有活跃的新闻节点 (假设 mode='News')
        # 注意：这里简化处理，假设 created_at 是 ISO 格式字符串
        # 实际生产中最好用 SQL 语句处理，这里用 Python 过滤
        res = supabase.table('nodes').select("*").eq('mode', 'News').execute()
        active_nodes = res.data
        
        sediment_count = 0
        now = datetime.now(timezone.utc)
        
        for node in active_nodes:
            created_at_str = node['created_at']
            # 处理时间格式
            try:
                if created_at_str.endswith('Z'):
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                else:
                    created_at = datetime.fromisoformat(created_at_str)
                
                # 计算年龄 (小时)
                age_hours = (now - created_at).total_seconds() / 3600
                
                # 设定生命周期：比如 2 分钟 (为了演示效果，设得很短！生产环境可以是 24 小时)
                TTL_HOURS = 0.05 # 3分钟后沉淀，方便你马上看到效果！
                
                if age_hours > TTL_HOURS:
                    # 沉淀它！
                    # 更新 mode 为 'Sediment'
                    supabase.table('nodes').update({"mode": "Sediment"}).eq("id", node['id']).execute()
                    sediment_count += 1
            except:
                continue
                
        return sediment_count
    except Exception as e:
        print(f"Time Decay Error: {e}")
        return 0
