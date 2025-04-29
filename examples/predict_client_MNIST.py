import requests
from torchvision import datasets, transforms
import random
import io
from PIL import Image

# Load MNIST test set (locally)
transform = transforms.Compose([
    transforms.ToTensor()
])

mnist_test = datasets.MNIST(root=".", train=False, download=True, transform=transform)

# Choose a random sample
idx = random.randint(0, len(mnist_test) - 1)
img_tensor, label = mnist_test[idx]

# Convert tensor to PIL Image
img = transforms.ToPILImage()(img_tensor)

# Save to a BytesIO buffer
buf = io.BytesIO()
img.save(buf, format="PNG")
buf.seek(0)

# Send POST request to /predict
response = requests.post(
    "http://localhost:5000/predict",
    files={"image": ("sample.png", buf, "image/png")}
)

print(f"Actual label: {label}")
print(f"Server response: {response.json()}")
