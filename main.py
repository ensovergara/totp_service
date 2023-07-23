import pyotp, redis, json
from typing import Protocol
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
rd = redis.Redis(host="localhost", port=6379, db=0)

#Const
PREFIX_DEVICE = 'devices_'
PREFIX_CODES = 'codes_'

#Models
class DeviceBase(BaseModel):
    """DeviceBase"""
    device_id: str

class Device(DeviceBase):
    """Device class"""
    key: str

class VerifyRequest(BaseModel):
    """Request for verify endpoint"""
    device_id: str
    check_code: str

#Services
class IRepository(Protocol):
    """Interface de servicio Repository"""
    def get_db(self, data:VerifyRequest|Device, prefix: str) -> bytes|None:
        """
        get data from  DB
        
        Parameters
        ----------
        data: VerifyRequest|Device
          objeto que contiene data como device_id y key para validar
        prefix: str
          prefijo que indica si buscar en device o code_validated

        Returns
        -------
        bytes | None 
          respuesta con datos o un valor None en caso de no encontrar key con data
        """

    def set_db(self, data:VerifyRequest|Device, prefix: str) -> bool|None:
        """
        Set data on DB
        
        Parameters
        ----------
        data: VerifyRequest|Device
          objeto que contiene data como device_id y key para validar
        prefix: str
          prefijo que indica si guardar en device o code_validated

        Returns
        -------
        True | False : bool
          respuesta boleana que indica si data fue guardada exitosamente o no
        """

class Repository(IRepository):
    """
    Clase que implementa IRepository
    """
    def get_db(self, data:VerifyRequest|Device, prefix: str):
        """ get data from db"""
        sufix = '_' + data.check_code if prefix == PREFIX_CODES else ''
        return rd.get(prefix + data.device_id +  sufix)

    def set_db(self, data:VerifyRequest|Device, prefix: str):
        """Set data in DB"""
        sufix = '_' + data.check_code if prefix == PREFIX_CODES else ''
        return rd.set(prefix + data.device_id + sufix, data.json(), ex=3600)


class ITotp(Protocol):
    """Interface de servicio TOTP"""
    def generate_key(self) -> str:
        """
        crea un key en 32bits y lo retorno en formato string
        """

    def check_totp_code(self, secret: str, code: str) -> bool:
        """
        Parameters
        ----------
        secret: str
          secreto para generar codigo para poder validar con codigo enviando
        code: str
          codigo enviado para validar si es correcto

        Returns
        -------
        True | False : bool
          respuesta boleana que indica si es codigo TOTP es válido o no segun secreto enviado
        """

class PytotpService(ITotp):
    """
    Clase que implementa servicios de TOTP
    """
    def generate_key(self) -> str:
        return pyotp.random_base32()

    def check_totp_code(self, secret: str, code: str) -> bool:
        print('secrete is ',  secret )
        totp = pyotp.TOTP(secret)
        now = totp.now()
        print("check_code:", code, "but code is: ", now)
        return totp.verify(code)

#Controllers
totp_service = PytotpService()
repository = Repository()
@app.get("/api/healthchecker")
def read_root():
    """healthchecker"""
    return {"message": "Welcome to TOTP service"}

@app.post("/register/")
async def create_device(device: DeviceBase):
    """Controller for create new register and shared_key"""
    key = totp_service.generate_key()
    new_device = Device(
        device_id = device.device_id,
        key = key,
    )
    repository.set_db(new_device, PREFIX_DEVICE)
    code_for_app = pyotp.totp.TOTP(key).provisioning_uri(
        name='totp@domain.com',
        issuer_name='Secure App TOTP'
      )
    print(code_for_app)
    return device

@app.post("/verify/")
async def check_code(verify: VerifyRequest):
    """Controller for verify code check"""
    data_device = repository.get_db(verify, PREFIX_DEVICE)
    print(data_device)
    if data_device:
        data = json.loads(data_device)
        print(data)
        secret = data['key']
        if totp_service.check_totp_code( secret , verify.check_code):
            code = repository.get_db(verify, PREFIX_CODES)
            if not code:
                repository.set_db(verify, PREFIX_CODES)
                return {"is_true": True}
            else:
                return {"is_true": False, "mesagge": "codigo ya fue utilizado"}
        else:
            return {"is_true": False}
    else:
        return {"is_true": False, "mesagge": "device_id no existe"}
