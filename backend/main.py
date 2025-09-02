from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def tradesafe_main():
    '''It will Initiate all process once it started'''
    return {"message": "tradesafe is online"}







