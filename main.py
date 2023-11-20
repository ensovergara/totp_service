import pyotp, redis, json
from typing import Protocol
from fastapi import FastAPI
from pydantic import BaseModel

import datetime

app = FastAPI()
rd = redis.Redis(host="localhost", password="pass-redis-stack",  port=6379, db=0)

#Const
PREFIX_User = 'Users_'
PREFIX_CODES = 'codes_'

#Models
class UserBase(BaseModel):
    """UserBase"""
    user_id: str

class User(UserBase):
    """User class"""
    shared_key: str

class VerifyRequest(BaseModel):
    """Request for verify endpoint"""
    user_id: str
    check_code: str

#Services
class IRepository(Protocol):
    """Interface de servicio Repository"""
    def get_db(self, data:VerifyRequest|User, prefix: str) -> bytes|None:
        """
        get data from  DB
        
        Parameters
        ----------
        data: VerifyRequest|User
          objeto que contiene data como user_id y shared_key para validar
        prefix: str
          prefijo que indica si buscar en User o code_validated

        Returns
        -------
        bytes | None 
          respuesta con datos o un valor None en caso de no encontrar shared_key con data
        """

    def set_db(self, data:VerifyRequest|User, prefix: str) -> bool|None:
        """
        Set data on DB
        
        Parameters
        ----------
        data: VerifyRequest|User
          objeto que contiene data como user_id y shared_key para validar
        prefix: str
          prefijo que indica si guardar en User o code_validated

        Returns
        -------
        True | False : bool
          respuesta boleana que indica si data fue guardada exitosamente o no
        """

class Repository(IRepository):
    """
    Clase que implementa IRepository
    """
    def get_db(self, data:VerifyRequest|User, prefix: str):
        """ get data from db"""
        sufix = '_' + data.check_code if prefix == PREFIX_CODES else ''
        return rd.get(prefix + data.user_id +  sufix)

    def set_db(self, data:VerifyRequest|User, prefix: str):
        """Set data in DB"""
        sufix = '_' + data.check_code if prefix == PREFIX_CODES else ''
        return rd.set(prefix + data.user_id + sufix, data.json(), ex=3600)

class ITotp(Protocol):
    """Interface de servicio TOTP"""
    def generate_shared_key(self) -> str:
        """
        crea un shared_key en 32bits y lo retorno en formato string
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
    def generate_shared_key(self) -> str:
        return pyotp.random_base32()

    def check_totp_code(self, secret: str, code: str) -> bool:
        print('secrete is ',  secret )

        diferencia_time = datetime.datetime.now() - datetime.timedelta(seconds=30)
        time_before = datetime.datetime.timestamp(diferencia_time)

        totp = pyotp.TOTP(secret)
        current_totp = totp.now()
        before_totp = totp.at(time_before)

        print("code send is:", code)
        print("and current code is: ", current_totp)
        print("and 30 seconds before was ", before_totp)

        return code in {current_totp, before_totp}

#Controllers
totp_service = PytotpService()
repository = Repository()
@app.get("/api/healthchecker")
def read_root():
    """healthchecker"""
    return {"message": "Welcome to PyTOTP service"}

@app.post("/register/")
async def create_User(user: UserBase):
    """Controller for create new register and shared_shared_key"""
    shared_key = totp_service.generate_shared_key()
    new_user = User(
        user_id = user.user_id,
        shared_key = shared_key,
    )
    repository.set_db(new_user, PREFIX_User)
    code_for_app = pyotp.totp.TOTP(shared_key).provisioning_uri(
        name='pytotp@domain.com',
        issuer_name='Sample secure App TOTP'
      )
    print(code_for_app)
    return {"shared_shared_key" : new_user.shared_key }

@app.post("/verify/")
async def check_code(verify: VerifyRequest):
    """Controller for verify code check"""
    data_user = repository.get_db(verify, PREFIX_User)
    print(data_user)
    if data_user:
        data = json.loads(data_user)
        print(data)
        secret = data['shared_key']
        if totp_service.check_totp_code( secret , verify.check_code):
            code = repository.get_db(verify, PREFIX_CODES)
            if not code:
                repository.set_db(verify, PREFIX_CODES)
                return {"is_true": True}
            else:
                return {"is_true": False, "mesagge": "code has already been used"}
        else:
            return {"is_true": False}
    else:
        return {"is_true": False, "mesagge": "user_id does not exist"}
