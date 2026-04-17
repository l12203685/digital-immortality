import sys, os
sys.stdout.reconfigure(encoding='utf-8')

all_files = set()
for root, dirs, files in os.walk('E:/投資交易/pla_md/'):
    for fname in files:
        if fname.endswith('.md'):
            full = os.path.join(root, fname)
            full = full.replace('\\', '/')
            all_files.add(full)

with open('C:/Users/admin/workspace/digital-immortality/results/digested_set.txt', 'r', encoding='utf-8') as f:
    digested = set(l.strip() for l in f if l.strip())

undigested = sorted(all_files - digested)
next30 = undigested[:30]

for path in next30:
    print(f'\n=== FILE: {path} ===')
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        print(content[:2000])
    except Exception as e:
        print(f'ERROR: {e}')
