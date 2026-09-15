from pydantic import BaseModel



class AIRequest(BaseModel):

    prompt: str


    device_info: dict = {

        "device_capability":"medium",

        "battery":80,

        "network_cost":0.2

    }