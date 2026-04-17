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
print(f'Total files found: {len(all_files)}')
print(f'Digested: {len(digested)}')
print(f'Undigested: {len(undigested)}')
print('First 35:')
for p in undigested[:35]:
    print(p)
