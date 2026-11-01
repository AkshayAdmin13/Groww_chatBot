import os

base = r'C:\Akshay\Next Leap\groww_chatbot'
dirs = [
    'config',
    'data/raw',
    'data/loaded',
    'data/chunks',
    'data/embeddings',
    'data/vectorstore',
    'src',
    'app'
]
for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)
print('directories created')
