import modal

app = modal.App("example-get-started")

@app.function()
def square(x):
    print("This code is running on a remote worker!")
    return x**2

@app.local_entrypoint()
def main():
    with app.run():
        print("the square is", square.remote(42))
      
  
main()


app = modal.App("GPU Check")
image = modal.Image.debian_slim().pip_install("torch")


# 
@app.function(gpu="T4", image=image)
def run():
    
    import torch
    print(torch.cuda.is_available())
    
@app.local_entrypoint()
def main():
    with app.run():
        print("Checking GPU")
      
  
main()
