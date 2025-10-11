import json

with open('./normal_sentences.json', 'r', encoding='utf-8') as f:
    content = f.read()
    sentences = json.loads(content)

for i in range(len(sentences)):
    sentences[i]['audio_path'] = f"src/assets/audio/sentence{i}.mp3"

with open('./normal_sentences.json', 'w', encoding='utf-8') as f:
    json.dump(sentences, f, ensure_ascii=False, indent=2)

print(f"Added audio_path to {len(sentences)} sentences")
