import xml.etree.ElementTree as ET

tree = ET.parse('../../data/trial/subtask1-homographic-test.xml')
root = tree.getroot()

for i, sent in enumerate(root):
    text = [word.text for word in sent]
    print(sent.attrib['id'], ' '.join(text))
