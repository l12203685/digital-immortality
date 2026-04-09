import json, sys

path = 'C:/Users/admin/GoogleDrive/聊天記錄/jsonl/202512.jsonl'
msgs = []
with open(path, encoding='utf-8') as f:
    for line in f:
        try:
            obj = json.loads(line)
            if '林盈宏' in obj.get('sender_name', '') and len(obj.get('content', '')) > 20:
                msgs.append(obj.get('content', ''))
        except:
            pass

print(f'Edward msgs: {len(msgs)}')
for i, m in enumerate(msgs[:15]):
    print(f'--- [{i}]')
    print(m[:250])
