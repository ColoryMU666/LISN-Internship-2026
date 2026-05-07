from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message" : "Hello world"}


def main():
    print("Hello from testfastapi!")


if __name__ == "__main__":
    main()
