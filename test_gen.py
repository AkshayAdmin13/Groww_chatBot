import sys
sys.path.insert(0, 'src')
from generate import Generator

g = Generator()
res = g.answer('What is the ELSS lock-in period?')
print(res['answer'])
print('SRC:', res['source_url'])
