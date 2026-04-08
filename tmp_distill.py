import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('jsonl_file', help='Path to the JSONL file')
parser.add_argument('--sender', default='林盈宏', help='Sender name to filter by')
parser.add_argument('--limit', type=int, default=15, help='Number of messages to print')
args = parser.parse_args()

msgs = []
with open(args.jsonl_file, encoding='utf-8') as f:
    for line in f:
        try:
            obj = json.loads(line)
            sender = obj.get('sender_name') or obj.get('s', '')
            content = obj.get('content') or obj.get('t', '')
            if args.sender in sender and len(content) > 20:
                msgs.append(content)
        except:
            pass

print(f'Edward msgs: {len(msgs)}')
for i, m in enumerate(msgs[:args.limit]):
    print(f'--- [{i}]')
    print(m[:250])
