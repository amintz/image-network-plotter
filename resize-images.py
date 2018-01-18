from PIL import Image

size = 200,200

testimg = Image.open('test.jpg')
testimg.thumbnail(size)
testimg.save('test-resized.jpg')
