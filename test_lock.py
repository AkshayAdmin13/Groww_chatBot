import sys
sys.path.insert(0, 'src')
from retrieve import Retriever

r = Retriever()
res = r.retrieve('What is the ELSS lock-in period?')
for x in res:
    if 'lock' in x['text'].lower():
        print(x['source_url'])
        print(x['text'][:250])
        break
else:
    print('not found')
    for x in res[:2]:
        print(x['source_url'])
        print(x['text'][:150])
        print('---')
